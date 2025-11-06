import pandas as pd
from datetime import datetime
import numpy as np

class LogPreprocessor:
    def __init__(self):
        self.working_hours_start = 9  # 9 AM
        self.working_hours_end = 17   # 5 PM

    def process_log_file(self, filepath):
        """Process the log file and return a cleaned DataFrame"""
        # Read the log file
        df = pd.read_csv(filepath)
        
        # Convert timestamp to datetime
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        
        # Add derived features
        df['Hour'] = df['Timestamp'].dt.hour
        df['DayOfWeek'] = df['Timestamp'].dt.dayofweek
        df['IsWorkingHours'] = df.apply(
            lambda x: 1 if self.working_hours_start <= x['Hour'] < self.working_hours_end 
            and x['DayOfWeek'] < 5 else 0, 
            axis=1
        )
        
        # Calculate access frequency per user
        df['AccessFrequency'] = df.groupby('UserID')['Timestamp'].transform('count')
        
        # Create features for model input
        df['IPHash'] = df['IP'].apply(hash)  # Simple hash for IP addresses
        
        return df

    def extract_features(self, df):
        """Extract numerical features for the model"""
        features = pd.DataFrame()
        
        # Numerical features
        features['hour'] = df['Hour']
        features['day_of_week'] = df['DayOfWeek']
        features['is_working_hours'] = df['IsWorkingHours']
        features['access_frequency'] = df['AccessFrequency']
        features['ip_hash'] = df['IPHash']
        
        # Normalize features
        for column in features.columns:
            features[column] = (features[column] - features[column].mean()) / features[column].std()
        
        return features