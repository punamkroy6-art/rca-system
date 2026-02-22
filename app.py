from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import os
from werkzeug.utils import secure_filename
from analyzer import RCAAnalyzer
from exporter import RCAExporter
from datetime import datetime
import uuid
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit
app.config['SECRET_KEY'] = 'supersecretkey'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'json'}

def allowed_file(filename):
    return '.' in filename and filename.lower().split('.')[-1] in ALLOWED_EXTENSIONS

analyzer = RCAAnalyzer()
exporter = RCAExporter()
# Temporary storage for prototype
# Persistence Store
REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)
reports_store = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"status": "Error", "message": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "Error", "message": "No selected file"}), 400

    analyzer = RCAAnalyzer()
    valid, df_or_message = analyzer.validate_file(file)
    if not valid:
        return jsonify({"status": "Error", "message": str(df_or_message)}), 400

    # Process and analyze
    try:
        df = df_or_message # Use the DF already loaded during validation
            
        results = analyzer.analyze(df)
        report_id = f"RCA-AUTO-{os.urandom(4).hex().upper()}"
        results["report_id"] = report_id
        results["filename"] = file.filename
        results["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Persist to disk
        reports_store[report_id] = results
        report_path = os.path.join(REPORTS_DIR, f"{report_id}.json")
        with open(report_path, 'w') as f:
            json.dump(results, f)

        return jsonify(results)
    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)}), 500

@app.route('/export/<format>/<report_id>')
def export(report_id, format):
    # Try to load from memory first, then disk
    results = reports_store.get(report_id)
    if not results:
        report_path = os.path.join(REPORTS_DIR, f"{report_id}.json")
        if os.path.exists(report_path):
            with open(report_path, 'r') as f:
                results = json.load(f)
                reports_store[report_id] = results
    
    if not results:
        return f"Report {report_id} not found", 404

    exporter = RCAExporter()
    try:
        if format == 'excel':
            filepath = exporter.to_excel(results, report_id)
            return send_file(filepath, as_attachment=True)
        elif format == 'pdf':
            filepath = exporter.to_pdf(results, report_id)
            return send_file(filepath, as_attachment=True)
    except Exception as e:
        return f"Export failed: {str(e)}", 500
    
    return "Invalid format", 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
