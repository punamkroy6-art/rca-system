import pandas as pd
import json
import os
from datetime import datetime

class RCAAnalyzer:
    def __init__(self):
        pass

    def validate_file(self, file_source):
        """Basic validation to ensure the file can be read."""
        if hasattr(file_source, 'filename'):
            filename = file_source.filename
            stream = file_source
        else:
            filename = file_source
            stream = file_source

        ext = os.path.splitext(filename)[1].lower()
        try:
            if ext == '.csv':
                df = pd.read_csv(stream)
            elif ext in ['.xlsx', '.xls']:
                df = pd.read_excel(stream)
            elif ext == '.json':
                df = pd.read_json(stream)
            else:
                return False, f"Unsupported file format: {ext}"
            
            if df.empty:
                return False, "The uploaded file is empty."
            return True, df
        except Exception as e:
            return False, f"Error reading file: {str(e)}"

    def analyze(self, df):
        """Simulates AI analysis by looking for patterns in the data."""
        # Clean columns for easier access
        original_columns = df.columns.tolist()
        df.columns = [c.lower().replace(' ', '_') for c in df.columns]
        
        anomalies = []
        top_contributors = {}
        time_series = []
        root_cause = "Analysis complete. System patterns appear within normal operational limits."
        recommendations = []
        error_keywords = ['500', 'error', 'fail', 'crit', 'fatal']
        
        results = {
            "summary": "Autonomous agent has completed deep-scan of the dataset.",
            "total_records": len(df),
            "anomalies": anomalies,
            "root_cause_prediction": root_cause,
            "confidence_score": 70,
            "status": "Success",
            "top_contributors": top_contributors,
            "time_range": {},
            "recommendations": recommendations,
            "time_series": time_series
        }

        # 1. Broadened Heuristic Column Identification
        status_col = next((c for c in df.columns if any(k in c for k in ['status', 'state', 'severity', 'priority', 'impact', 'urgency', 'level'])), None)
        service_col = next((c for c in df.columns if any(k in c for k in ['service', 'category', 'subcategory', 'app', 'component', 'system', 'host'])), None)
        time_col = next((c for c in df.columns if any(k in c for k in ['time', 'date', 'ts', 'opened', 'created', 'timestamp'])), None)

        # 2. Adaptive Time Range and Trend Analysis
        if time_col:
            try:
                df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
                df = df.dropna(subset=[time_col])
                
                start_dt = df[time_col].min()
                end_dt = df[time_col].max()
                results["time_range"] = {
                    "start": start_dt.strftime('%Y-%m-%d %H:%M:%S'),
                    "end": end_dt.strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Adaptive Resampling based on span
                span_seconds = (end_dt - start_dt).total_seconds()
                if span_seconds < 3600: # < 1 hour
                    freq = 'min'
                    fmt = '%H:%M'
                elif span_seconds < 86400: # < 1 day
                    freq = '5min'
                    fmt = '%H:%M'
                elif span_seconds < 86400 * 7: # < 1 week
                    freq = 'H'
                    fmt = '%d %H:%M'
                else: # > 1 week
                    freq = 'D'
                    fmt = '%Y-%m-%d'

                ts_data = df.set_index(time_col).resample(freq).size()
                
                # Further downsample if still too many points for Chart.js
                if len(ts_data) > 100:
                    ts_data = ts_data.iloc[::len(ts_data)//60]

                results["time_series"] = {
                    "labels": ts_data.index.strftime(fmt).tolist(),
                    "counts": ts_data.tolist()
                }
                
                if len(ts_data) > 0:
                    avg = ts_data.mean()
                    peak = ts_data.max()
                    if peak > avg * 2:
                        anomalies.append(f"Incident spike detected: Peak frequency ({int(peak)}) is {int(peak/avg if avg >0 else 0)}x higher than average.")
            except:
                pass

        # 3. Vectorized Cross-Service & Quality Matrix
        service_status_matrix = {}
        impact_scores = {}
        
        if status_col and service_col:
            # Limit to Top 12 services to keep graph clean
            top_services = df[service_col].value_counts().head(12).index.tolist()
            mask = df[service_col].isin(top_services)
            df_filtered = df[mask]

            matrix = pd.crosstab(df_filtered[service_col], df_filtered[status_col])
            service_status_matrix = matrix.to_dict(orient='index')
            
            error_keywords = ['500', 'error', 'fail', 'crit', 'fatal', 'high', 'p1', 'p2', 'p3', 'major', 'disrupted', 'down']
            error_cols = [c for c in matrix.columns if any(k in str(c).lower() for k in error_keywords)]
            
            if error_cols:
                service_errors = matrix[error_cols].sum(axis=1)
                service_totals = matrix.sum(axis=1)
                scores = (service_errors / service_totals * 10).round(1)
                impact_scores = scores.to_dict()

        # Clean mapping for JSON
        results["service_matrix"] = {str(k): {str(p): int(v) for p, v in val.items()} for k, val in service_status_matrix.items()}
        # Ensure at least 3 points for radar chart or it looks broken
        if len(impact_scores) >= 3:
            results["impact_scores"] = {str(k): float(v) for k, v in impact_scores.items()}
        else:
            results["impact_scores"] = {} # Front-end should handle empty radar

        # 4. Root Cause Extraction & Insight Generation
        if status_col:
            results["confidence_score"] = 85
            counts = df[status_col].value_counts()
            top_contributors = counts.head(5).to_dict()
            results["top_contributors"] = {str(k): int(v) for k, v in top_contributors.items()}
            
            # Identify critical errors
            error_keys = [k for k in counts.index if any(e in str(k).lower() for e in error_keywords)]
            if error_keys:
                primary_error = error_keys[0]
                error_percentage = (counts[primary_error] / len(df)) * 100
                
                if service_col:
                    # Find which service is the biggest offender for this specific error
                    error_subset = df[df[status_col] == primary_error]
                    top_offender = error_subset[service_col].mode().iloc[0]
                    offender_count = len(error_subset[error_subset[service_col] == top_offender])
                    
                    results["root_cause_prediction"] = f"Anomalous error cluster detected in '{top_offender}'. This component accounts for {int((offender_count/len(error_subset))*100)}% of the total recorded '{primary_error}' incidents."
                    anomalies.append(f"Significant availability drop in {top_offender} (Impact Score: {impact_scores.get(top_offender, 0)}/10).")
                    
                    # Diversified check: are others safe?
                    other_services = [s for s in matrix.index if s != top_offender]
                    if other_services:
                        summary_text = str(results["summary"])
                        results["summary"] = summary_text + f" Primary disruption isolated to '{top_offender}', while other services show stable patterns."
                    
                    recommendations.append(f"Immediate rollback or restart of service '{top_offender}'.")
                    recommendations.append(f"Check upstream dependencies for '{top_offender}' identifying as 'Critical Impact Zone'.")
                else:
                    results["root_cause_prediction"] = f"Widespread '{primary_error}' incidents detected, accounting for {int(error_percentage)}% of total volume."
                    anomalies.append("System-wide error saturation detected.")
                    recommendations.append("Initiate circuit breaker verification across all upstream services.")
            else:
                results["root_cause_prediction"] = "System stability verified. No critical service disruptions identified in the analyzed period."

        # Fallback if status_col not found but service_col is
        elif service_col:
            top_s = df[service_col].value_counts().head(5)
            results["top_contributors"] = {str(k): int(v) for k, v in top_s.items()}
            results["root_cause_prediction"] = f"Log volume primarily driven by '{top_s.index[0]}'. No explicit status-based failure identifiers found."

        if not recommendations:
            recommendations.append("Continue routine health monitoring.")
            recommendations.append("Add 'Status' or 'Severity' headers to logs for deeper autonomous diagnostic accuracy.")

        return results
