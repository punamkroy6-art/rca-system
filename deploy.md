# Deployment Guide: Autonomous RCA System

This guide provides instructions for deploying the RCA system in a production environment using Docker.

## Prerequisites
- **Docker** and **Docker Compose** installed on your server.
- Basic familiarity with terminal/command line.

## 1. Quick Deploy (Docker)
The easiest way to deploy is using the provided Dockerfile.

### Build and Run
```bash
# Build the image
docker build -t rca-system:latest .

# Run the container
docker run -d \
  -p 5000:5000 \
  --name rca-instance \
  -v rca_data:/app/data \
  -v rca_exports:/app/exports \
  rca-system:latest
```

## 2. Production Considerations
- **Storage**: We use Docker volumes (`rca_data`, `rca_exports`) to ensure analysis reports persist even if the container is restarted.
- **Port**: The application listens on port `5000`. You may want to put a reverse proxy (like Nginx) in front of it for SSL/HTTPS support.
- **Memory**: Ensure the server has at least 2GB of RAM for smooth processing of 20k+ log datasets.

## 3. Local (No Docker)
If you prefer not to use Docker, follow these steps:
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run with Gunicorn (Linux/macOS)
gunicorn --bind 0.0.0.0:5000 wsgi:app

# 3. Run on Windows (Development mode)
python app.py
```

## 7. Google Cloud Run (Detailed Windows Steps)

### Step 1: Install the SDK
1.  **Download**: Click here to download the [Google Cloud SDK Installer](https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe).
2.  **Run**: Open the downloaded file and follow the setup wizard.
3.  **Complete**: At the end, keep the box "Start Google Cloud SDK Shell" checked and click Finish.

### Step 2: Initialize GCP
In the new window that opens (the Google Cloud SDK Shell), run:
```bash
gcloud init
```
-   It will open a browser to log you in.
-   **Important**: Make sure you select a "Project ID" during this step.

### How to Fix "project not specified"
If you get an error saying the project is not specified, run this command to tell Google which project to use:
```bash
gcloud config set project [YOUR_PROJECT_ID]
```
*(Replace `[YOUR_PROJECT_ID]` with the ID of your Google Cloud project.)*

### Step 3: Deployment
Navigate to your project folder:
```powershell
cd c:\Users\punam\antigravity
```

Deploy the app:
```bash
gcloud run deploy rca-system --source . --region us-central1 --allow-unauthenticated
```
-   **Note**: If it asks for "Service Account" or "APIs", type `y` (Yes).

---

## Comparison of Platforms

## 5. Kubernetes Deployment (Cloud-Native)
For scalable cloud deployment, use the provided manifests in the `k8s/` directory.

### Step 1: Create Persistence
```bash
kubectl apply -f k8s/pvc.yaml
```

### Step 2: Deploy Application
```bash
# Ensure your image is pushed to a registry (e.g. Docker Hub, ECR)
# Update k8s/deployment.yaml with the correct image tag
kubectl apply -f k8s/deployment.yaml
```

### Step 3: Expose Service
```bash
kubectl apply -f k8s/service.yaml
```

### Step 4: Access
```bash
# Get the external IP (if using LoadBalancer)
kubectl get service rca-service
```

## 6. Replit Deployment (Step-by-Step)

### Where are my files?
All your project files are located in:  
`c:\Users\punam\antigravity`

### How to Upload & Run in Replit

1.  **Prepare Files**:
    *   Open your file explorer to `c:\Users\punam\antigravity`.
    *   Select all files (Ctrl+A).
    *   Right-click -> **Compress to ZIP file** (name it `rca_system.zip`).

2.  **Upload to Replit**:
    *   Open [Replit.com](https://replit.com) and log in.
    *   Click **+ Create Repl**.
    *   Choose **Template: Python** (don't worry about the template, we will replace the files).
    *   On the left sidebar, click the **Files** icon.
    *   Drag and drop your `rca_system.zip` into the file area.
    *   Click the **three dots** next to the ZIP and select **Extract**.

3.  **Run with One Click**:
    *   Click the **Run** button at the top.
    *   Replit will read the `.replit` file I created and automatically install all dependencies (from `requirements.txt`) and start the server.

### Accessing the Dashboard
- A "Webview" window will appear in Replit once it starts.
- Use the provided URL (e.g., `https://rca-system.username.repl.co`) to access it from any browser.

Oro
