from flask import Flask, render_template, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import pandas as pd
from models.detector import AnomalyDetector
from models.preprocessor import LogPreprocessor

app = Flask(__name__)

# Set up absolute paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'anomalies.db')
UPLOAD_PATH = os.path.join(BASE_DIR, 'data', 'uploads')

# Ensure directories exist
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
os.makedirs(UPLOAD_PATH, exist_ok=True)

# Configure Flask app
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['UPLOAD_FOLDER'] = UPLOAD_PATH
db = SQLAlchemy(app)

class Anomaly(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    action = db.Column(db.String(100))
    resource = db.Column(db.String(200))
    ip_address = db.Column(db.String(50))
    anomaly_type = db.Column(db.String(100))
    score = db.Column(db.Float)

# Initialize database
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    try:
        # Save the file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Process the log file
        preprocessor = LogPreprocessor()
        detector = AnomalyDetector()

        # Preprocess data
        df = preprocessor.process_log_file(filepath)
        
        # Detect anomalies
        anomalies = detector.detect(df)

        # Store anomalies in database
        for _, row in anomalies.iterrows():
            anomaly = Anomaly(
                user_id=row['UserID'],
                timestamp=pd.to_datetime(row['Timestamp']),
                action=row['Action'],
                resource=row['Resource'],
                ip_address=row['IP'],
                anomaly_type=row['AnomalyType'],
                score=row['AnomalyScore']
            )
            db.session.add(anomaly)
        
        db.session.commit()

        return jsonify({
            'message': 'File processed successfully',
            'anomalies_count': len(anomalies)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/anomalies')
def get_anomalies():
    anomalies = Anomaly.query.all()
    return jsonify([{
        'user_id': a.user_id,
        'timestamp': a.timestamp.isoformat(),
        'action': a.action,
        'resource': a.resource,
        'ip_address': a.ip_address,
        'anomaly_type': a.anomaly_type,
        'score': a.score
    } for a in anomalies])

@app.route('/export')
def export_anomalies():
    format_type = request.args.get('format', 'csv')
    
    anomalies = Anomaly.query.all()
    df = pd.DataFrame([{
        'user_id': a.user_id,
        'timestamp': a.timestamp,
        'action': a.action,
        'resource': a.resource,
        'ip_address': a.ip_address,
        'anomaly_type': a.anomaly_type,
        'score': a.score
    } for a in anomalies])
    
    if format_type == 'csv':
        output = os.path.join(app.config['UPLOAD_FOLDER'], 'anomalies.csv')
        df.to_csv(output, index=False)
        return send_file(output, as_attachment=True)
    else:
        return jsonify({'error': 'Format not supported'}), 400

if __name__ == '__main__':
    app.run(debug=True)