# Insider Threat Detection System

A web-based application that uses AI to detect insider threats from access logs and displays anomalies on an interactive dashboard. Optimized for macOS with Apple Silicon.

## Features

- AI-powered anomaly detection in access logs
- Interactive web dashboard
- Real-time log file processing
- Automated threat detection
- Visualization of user activity patterns
- Export functionality for reports
- Optimized for Apple Silicon

## Prerequisites

- macOS with Apple Silicon
- Python 3.11+
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git init
git add .
git commit -m "Initial commit"
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Project Structure

```
project/
├── app.py                 # Main Flask application
├── models/
│   ├── __init__.py
│   ├── detector.py       # Anomaly detection model
│   └── preprocessor.py   # Data preprocessing utilities
├── static/
│   ├── css/             # Stylesheets
│   └── js/              # JavaScript files
├── templates/           # HTML templates
├── data/               # Sample data and database
└── requirements.txt    # Project dependencies
```

## Usage

1. Start the Flask application:
```bash
python app.py
```

2. Open a web browser and navigate to `http://localhost:5000`

3. Upload your access log file through the web interface

4. View the analysis results and anomaly detections in the dashboard

## Model Details

The system uses a combination of:
- Isolation Forest for anomaly detection
- Time-series analysis for behavior patterns
- Core ML optimization for Apple Silicon

## License

MIT License