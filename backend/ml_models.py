"""
Machine Learning Models for Ad Performance Prediction
"""
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta


class MLModels:
    """
    ML models for predictions, trend detection, and clustering
    """
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self._prepare_data()
        self.models = {}
        self.scaler = StandardScaler()
    
    def _prepare_data(self):
        """Prepare data for ML models"""
        # Ensure date is datetime
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.df = self.df.sort_values('date')
        
        # Create time-based features
        self.df['day_of_week'] = self.df['date'].dt.dayofweek
        self.df['day_of_month'] = self.df['date'].dt.day
        self.df['days_since_start'] = (self.df['date'] - self.df['date'].min()).dt.days
        
        # Ensure numeric columns
        numeric_cols = ['impressions', 'clicks', 'spend', 'conversions', 'revenue']
        for col in numeric_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce').fillna(0)
    
    def _prepare_features(self, target_col: str = 'revenue') -> tuple:
        """Prepare features for training"""
        if target_col not in self.df.columns:
            # Fallback to conversions or clicks
            if 'conversions' in self.df.columns:
                target_col = 'conversions'
            else:
                target_col = 'clicks'
        
        # Aggregate by date for time series
        daily = self.df.groupby('date').agg({
            'spend': 'sum',
            'impressions': 'sum',
            'clicks': 'sum',
            'conversions': 'sum' if 'conversions' in self.df.columns else 'sum',
            'revenue': 'sum' if 'revenue' in self.df.columns else 'sum',
            'day_of_week': 'first',
            'day_of_month': 'first',
            'days_since_start': 'first'
        }).reset_index()
        
        # Features
        feature_cols = ['spend', 'impressions', 'clicks', 'day_of_week', 'day_of_month', 'days_since_start']
        if 'conversions' in daily.columns and target_col != 'conversions':
            feature_cols.append('conversions')
        if 'revenue' in daily.columns and target_col != 'revenue':
            feature_cols.append('revenue')
        
        X = daily[feature_cols].values
        y = daily[target_col].values
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        return X_scaled, y, daily, feature_cols
    
    def train_prediction_model(self, target: str = 'revenue') -> Dict[str, Any]:
        """
        Train regression model to predict future performance
        Returns model performance metrics
        """
        try:
            X, y, daily, feature_cols = self._prepare_features(target)
            
            if len(X) < 7:  # Need minimum data points
                return {
                    'model_type': 'insufficient_data',
                    'message': 'Not enough data points for training'
                }
            
            # Split data (80% train, 20% test)
            split_idx = int(len(X) * 0.8)
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]
            
            # Train model
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            
            # Evaluate
            train_score = model.score(X_train, y_train)
            test_score = model.score(X_test, y_test)
            
            # Store model
            self.models[target] = {
                'model': model,
                'feature_cols': feature_cols,
                'target': target
            }
            
            return {
                'model_type': 'random_forest',
                'target': target,
                'train_score': float(train_score),
                'test_score': float(test_score),
                'feature_importance': dict(zip(feature_cols, model.feature_importances_.tolist()))
            }
        
        except Exception as e:
            return {
                'model_type': 'error',
                'message': str(e)
            }
    
    def predict_future(self, days_ahead: int = 7) -> Dict[str, Any]:
        """
        Predict future performance for next N days
        """
        predictions = {}
        
        # Try to predict revenue if available
        if 'revenue' in self.df.columns:
            if 'revenue' not in self.models:
                self.train_prediction_model('revenue')
            
            if 'revenue' in self.models:
                pred = self._predict_target('revenue', days_ahead)
                predictions['revenue'] = pred
        
        # Try to predict conversions if available
        if 'conversions' in self.df.columns:
            if 'conversions' not in self.models:
                self.train_prediction_model('conversions')
            
            if 'conversions' in self.models:
                pred = self._predict_target('conversions', days_ahead)
                predictions['conversions'] = pred
        
        return predictions
    
    def _predict_target(self, target: str, days_ahead: int) -> List[Dict]:
        """Helper to predict a specific target"""
        model_info = self.models[target]
        model = model_info['model']
        feature_cols = model_info['feature_cols']
        
        # Get last date
        last_date = self.df['date'].max()
        
        # Get recent averages for features
        recent = self.df[self.df['date'] >= (last_date - timedelta(days=7))]
        avg_spend = recent['spend'].mean()
        avg_impressions = recent['impressions'].mean()
        avg_clicks = recent['clicks'].mean()
        
        predictions = []
        for i in range(days_ahead):
            future_date = last_date + timedelta(days=i+1)
            day_of_week = future_date.weekday()
            day_of_month = future_date.day
            days_since_start = (future_date - self.df['date'].min()).days
            
            # Build feature vector
            features = []
            for col in feature_cols:
                if col == 'spend':
                    features.append(avg_spend)
                elif col == 'impressions':
                    features.append(avg_impressions)
                elif col == 'clicks':
                    features.append(avg_clicks)
                elif col == 'day_of_week':
                    features.append(day_of_week)
                elif col == 'day_of_month':
                    features.append(day_of_month)
                elif col == 'days_since_start':
                    features.append(days_since_start)
                elif col in ['conversions', 'revenue']:
                    # Use recent average
                    features.append(recent[col].mean() if col in recent.columns else 0)
                else:
                    features.append(0)
            
            # Scale and predict
            features_scaled = self.scaler.transform([features])
            pred_value = model.predict(features_scaled)[0]
            
            predictions.append({
                'date': future_date.isoformat(),
                'predicted_value': float(max(0, pred_value))  # Ensure non-negative
            })
        
        return predictions
    
    def detect_trends(self) -> Dict[str, Any]:
        """
        Detect performance trends using statistical methods
        """
        daily = self.df.groupby('date').agg({
            'spend': 'sum',
            'revenue': 'sum' if 'revenue' in self.df.columns else 'sum',
            'conversions': 'sum' if 'conversions' in self.df.columns else 'sum',
            'clicks': 'sum'
        }).reset_index()
        
        trends = {}
        
        for metric in ['spend', 'revenue', 'conversions', 'clicks']:
            if metric in daily.columns:
                values = daily[metric].values
                if len(values) >= 7:  # Need minimum data
                    # Simple linear trend
                    x = np.arange(len(values))
                    slope, intercept = np.polyfit(x, values, 1)
                    
                    # Calculate R-squared
                    y_pred = slope * x + intercept
                    ss_res = np.sum((values - y_pred) ** 2)
                    ss_tot = np.sum((values - np.mean(values)) ** 2)
                    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
                    
                    # Percentage change
                    pct_change = ((values[-1] - values[0]) / values[0] * 100) if values[0] > 0 else 0
                    
                    trends[metric] = {
                        'slope': float(slope),
                        'direction': 'increasing' if slope > 0 else 'decreasing',
                        'r_squared': float(r_squared),
                        'pct_change': float(pct_change),
                        'strength': 'strong' if abs(r_squared) > 0.5 else 'weak'
                    }
        
        return trends
    
    def cluster_ads(self, n_clusters: int = 3) -> Dict[str, Any]:
        """
        Cluster ads by performance behavior
        """
        if 'ad_name' in self.df.columns:
            group_col = 'ad_name'
        elif 'campaign_name' in self.df.columns:
            group_col = 'campaign_name'
        else:
            return {'error': 'No ad_name or campaign_name column found'}
        
        # Aggregate by ad
        ad_data = self.df.groupby(group_col).agg({
            'spend': 'sum',
            'revenue': 'sum' if 'revenue' in self.df.columns else 'sum',
            'conversions': 'sum' if 'conversions' in self.df.columns else 'sum',
            'clicks': 'sum',
            'impressions': 'sum'
        }).reset_index()
        
        # Calculate metrics
        ad_data['ctr'] = ad_data.apply(
            lambda x: (x['clicks'] / x['impressions'] * 100) if x['impressions'] > 0 else 0,
            axis=1
        )
        
        if 'revenue' in ad_data.columns:
            ad_data['roas'] = ad_data.apply(
                lambda x: x['revenue'] / x['spend'] if x['spend'] > 0 else 0,
                axis=1
            )
        
        # Features for clustering
        feature_cols = ['spend', 'ctr']
        if 'roas' in ad_data.columns:
            feature_cols.append('roas')
        if 'conversions' in ad_data.columns:
            feature_cols.append('conversions')
        
        if len(ad_data) < n_clusters:
            return {'error': f'Not enough ads to cluster into {n_clusters} groups'}
        
        X = ad_data[feature_cols].values
        X_scaled = self.scaler.fit_transform(X)
        
        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        ad_data['cluster'] = kmeans.fit_predict(X_scaled)
        
        # Describe clusters
        cluster_summary = []
        for cluster_id in range(n_clusters):
            cluster_ads = ad_data[ad_data['cluster'] == cluster_id]
            cluster_summary.append({
                'cluster_id': int(cluster_id),
                'ad_count': len(cluster_ads),
                'avg_spend': float(cluster_ads['spend'].mean()),
                'avg_ctr': float(cluster_ads['ctr'].mean()),
                'avg_roas': float(cluster_ads['roas'].mean()) if 'roas' in cluster_ads.columns else None,
                'ads': cluster_ads[group_col].tolist()
            })
        
        return {
            'n_clusters': n_clusters,
            'clusters': cluster_summary,
            'ad_clusters': ad_data[[group_col, 'cluster']].to_dict('records')
        }

