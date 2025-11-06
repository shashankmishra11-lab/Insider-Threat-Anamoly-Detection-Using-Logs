from sklearn.ensemble import IsolationForest
import numpy as np
import pandas as pd
import tensorflow as tf
import coremltools as ct
from sklearn.preprocessing import StandardScaler

class AnomalyDetector:
    def __init__(self):
        self.isolation_forest = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_jobs=-1
        )
        self.scaler = StandardScaler()
        
    def detect(self, df):
        """Detect anomalies in the preprocessed data"""
        # Extract features for anomaly detection
        features = self._prepare_features(df)
        
        # Fit and predict using Isolation Forest
        anomaly_scores = self.isolation_forest.fit_predict(features)
        
        # Convert predictions to anomaly types
        anomalies = df.copy()
        anomalies['AnomalyScore'] = self._normalize_scores(
            self.isolation_forest.score_samples(features)
        )
        
        # Determine anomaly types
        anomalies['AnomalyType'] = self._categorize_anomalies(df, anomaly_scores)
        
        # Filter only anomalous entries
        return anomalies[anomalies['AnomalyType'] != 'Normal']
    
    def _prepare_features(self, df):
        """Prepare features for the model"""
        features = pd.DataFrame()
        
        # Time-based features
        features['hour'] = df['Hour']
        features['day_of_week'] = df['DayOfWeek']
        features['is_working_hours'] = df['IsWorkingHours']
        
        # Activity-based features
        features['access_frequency'] = df['AccessFrequency']
        features['ip_hash'] = df['IPHash']
        
        # Standardize features
        return self.scaler.fit_transform(features)
    
    def _normalize_scores(self, scores):
        """Normalize anomaly scores to range [0,1]"""
        return (scores - np.min(scores)) / (np.max(scores) - np.min(scores))
    
    def _categorize_anomalies(self, df, anomaly_scores):
        """Categorize anomalies based on the violation type"""
        categories = []
        
        for idx, row in df.iterrows():
            if anomaly_scores[idx] == -1:  # Anomaly detected
                if row['IsWorkingHours'] == 0:
                    categories.append('Outside Working Hours')
                elif row['AccessFrequency'] > df['AccessFrequency'].quantile(0.95):
                    categories.append('High Access Frequency')
                else:
                    categories.append('Unusual IP/Location')
            else:
                categories.append('Normal')
        
        return categories
    
    def export_to_coreml(self, model_path='models/anomaly_detector.mlmodel'):
        """Export the trained model to CoreML format"""
        # Create a simple TensorFlow model wrapper
        tf_model = tf.keras.Sequential([
            tf.keras.layers.Dense(
                units=1,
                activation='sigmoid',
                input_shape=(5,)  # Number of features
            )
        ])
        
        # Convert to CoreML
        model = ct.convert(
            tf_model,
            inputs=[ct.TensorType(shape=(1, 5))],
            minimum_deployment_target=ct.target.macOS13
        )
        
        # Save the model
        model.save(model_path)