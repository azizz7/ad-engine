"""
Analytics Engine - Computes key performance metrics
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any


class AnalyticsEngine:
    """
    Computes business metrics from ad performance data
    """
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self._prepare_data()
    
    def _serialize_for_json(self, data: List[Dict]) -> List[Dict]:
        """Ensure all values in dict list are JSON serializable"""
        serialized = []
        for record in data:
            serialized_record = {}
            for key, value in record.items():
                if pd.isna(value):
                    serialized_record[key] = None
                elif isinstance(value, (np.integer, np.int64, np.int32)):
                    serialized_record[key] = int(value)
                elif isinstance(value, (np.floating, np.float64, np.float32)):
                    serialized_record[key] = float(value)
                elif isinstance(value, np.ndarray):
                    serialized_record[key] = value.tolist()
                elif isinstance(value, pd.Timestamp):
                    serialized_record[key] = value.isoformat()
                elif value == float('inf') or value == float('-inf'):
                    serialized_record[key] = None
                else:
                    serialized_record[key] = value
            serialized.append(serialized_record)
        return serialized
    
    def _prepare_data(self):
        """Prepare and clean data for analysis"""
        # Ensure numeric columns
        numeric_cols = ['impressions', 'clicks', 'spend', 'conversions', 'revenue']
        for col in numeric_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce').fillna(0)
    
    def compute_ctr(self) -> float:
        """Compute overall Click-Through Rate"""
        total_clicks = self.df['clicks'].sum()
        total_impressions = self.df['impressions'].sum()
        if total_impressions == 0:
            return 0.0
        return (total_clicks / total_impressions) * 100
    
    def compute_cpc(self) -> float:
        """Compute overall Cost Per Click"""
        total_clicks = self.df['clicks'].sum()
        total_spend = self.df['spend'].sum()
        if total_clicks == 0:
            return 0.0
        return total_spend / total_clicks
    
    def compute_cpa(self) -> float:
        """Compute overall Cost Per Acquisition"""
        if 'conversions' not in self.df.columns:
            return None
        total_conversions = self.df['conversions'].sum()
        total_spend = self.df['spend'].sum()
        if total_conversions == 0:
            return None
        return total_spend / total_conversions
    
    def compute_roas(self) -> float:
        """Compute overall Return on Ad Spend"""
        if 'revenue' not in self.df.columns:
            return None
        total_revenue = self.df['revenue'].sum()
        total_spend = self.df['spend'].sum()
        if total_spend == 0:
            return None
        return total_revenue / total_spend
    
    def get_best_performing_ads(self, metric: str = 'roas', limit: int = 5) -> List[Dict]:
        """Get top performing ads by specified metric"""
        if 'ad_name' in self.df.columns:
            group_col = 'ad_name'
        elif 'campaign_name' in self.df.columns:
            group_col = 'campaign_name'
        else:
            return []
        
        grouped = self.df.groupby(group_col).agg({
            'spend': 'sum',
            'revenue': 'sum' if 'revenue' in self.df.columns else 'sum',
            'conversions': 'sum' if 'conversions' in self.df.columns else 'sum',
            'clicks': 'sum',
            'impressions': 'sum'
        }).reset_index()
        
        # Calculate metric
        if metric == 'roas' and 'revenue' in self.df.columns:
            grouped['metric_value'] = grouped.apply(
                lambda x: x['revenue'] / x['spend'] if x['spend'] > 0 else 0,
                axis=1
            )
        elif metric == 'cpa' and 'conversions' in self.df.columns:
            grouped['metric_value'] = grouped.apply(
                lambda x: x['spend'] / x['conversions'] if x['conversions'] > 0 else float('inf'),
                axis=1
            )
            # Lower is better for CPA
            grouped = grouped.sort_values('metric_value').head(limit)
            return self._serialize_for_json(grouped.to_dict('records'))
        elif metric == 'ctr':
            grouped['metric_value'] = grouped.apply(
                lambda x: (x['clicks'] / x['impressions'] * 100) if x['impressions'] > 0 else 0,
                axis=1
            )
        else:
            return []
        
        # Sort and return top
        grouped = grouped.sort_values('metric_value', ascending=False).head(limit)
        return self._serialize_for_json(grouped.to_dict('records'))
    
    def get_worst_performing_ads(self, metric: str = 'roas', limit: int = 5) -> List[Dict]:
        """Get worst performing ads by specified metric"""
        if 'ad_name' in self.df.columns:
            group_col = 'ad_name'
        elif 'campaign_name' in self.df.columns:
            group_col = 'campaign_name'
        else:
            return []
        
        grouped = self.df.groupby(group_col).agg({
            'spend': 'sum',
            'revenue': 'sum' if 'revenue' in self.df.columns else 'sum',
            'conversions': 'sum' if 'conversions' in self.df.columns else 'sum',
            'clicks': 'sum',
            'impressions': 'sum'
        }).reset_index()
        
        # Calculate metric
        if metric == 'roas' and 'revenue' in self.df.columns:
            grouped['metric_value'] = grouped.apply(
                lambda x: x['revenue'] / x['spend'] if x['spend'] > 0 else 0,
                axis=1
            )
            grouped = grouped.sort_values('metric_value', ascending=True).head(limit)
        elif metric == 'cpa' and 'conversions' in self.df.columns:
            grouped['metric_value'] = grouped.apply(
                lambda x: x['spend'] / x['conversions'] if x['conversions'] > 0 else float('inf'),
                axis=1
            )
            # Higher is worse for CPA
            grouped = grouped.sort_values('metric_value', ascending=False).head(limit)
        elif metric == 'ctr':
            grouped['metric_value'] = grouped.apply(
                lambda x: (x['clicks'] / x['impressions'] * 100) if x['impressions'] > 0 else 0,
                axis=1
            )
            grouped = grouped.sort_values('metric_value', ascending=True).head(limit)
        else:
            return []
        
        return self._serialize_for_json(grouped.to_dict('records'))
    
    def identify_spend_inefficiencies(self, threshold_roas: float = 1.0) -> List[Dict]:
        """Identify ads with high spend but low ROAS"""
        if 'revenue' not in self.df.columns:
            return []
        
        if 'ad_name' in self.df.columns:
            group_col = 'ad_name'
        elif 'campaign_name' in self.df.columns:
            group_col = 'campaign_name'
        else:
            return []
        
        grouped = self.df.groupby(group_col).agg({
            'spend': 'sum',
            'revenue': 'sum'
        }).reset_index()
        
        grouped['roas'] = grouped.apply(
            lambda x: x['revenue'] / x['spend'] if x['spend'] > 0 else 0,
            axis=1
        )
        
        # Filter for high spend, low ROAS
        inefficiencies = grouped[
            (grouped['spend'] > grouped['spend'].quantile(0.5)) &  # Top 50% by spend
            (grouped['roas'] < threshold_roas)
        ].sort_values('spend', ascending=False)
        
        return self._serialize_for_json(inefficiencies.to_dict('records'))
    
    def compute_trends(self) -> Dict[str, Any]:
        """Compute performance trends over time"""
        daily = self.df.groupby('date').agg({
            'spend': 'sum',
            'revenue': 'sum' if 'revenue' in self.df.columns else 'sum',
            'conversions': 'sum' if 'conversions' in self.df.columns else 'sum',
            'clicks': 'sum',
            'impressions': 'sum'
        }).reset_index()
        
        daily['ctr'] = daily.apply(
            lambda x: (x['clicks'] / x['impressions'] * 100) if x['impressions'] > 0 else 0,
            axis=1
        )
        
        if 'revenue' in self.df.columns:
            daily['roas'] = daily.apply(
                lambda x: x['revenue'] / x['spend'] if x['spend'] > 0 else 0,
                axis=1
            )
        
        # Calculate trend direction (simple linear regression slope)
        trends = {}
        for metric in ['spend', 'revenue', 'conversions', 'ctr', 'roas']:
            if metric in daily.columns:
                values = daily[metric].values
                if len(values) > 1:
                    x = np.arange(len(values))
                    slope = np.polyfit(x, values, 1)[0]
                    trends[metric] = {
                        'slope': float(slope),
                        'direction': 'increasing' if slope > 0 else 'decreasing',
                        'strength': 'strong' if abs(slope) > np.std(values) else 'weak'
                    }
        
        # Convert date to string for JSON serialization
        daily['date'] = daily['date'].dt.strftime('%Y-%m-%d')
        
        # Convert to dict and ensure all values are JSON serializable
        daily_data = self._serialize_for_json(daily.to_dict('records'))
        
        return {
            'daily_data': daily_data,
            'trends': trends
        }
    
    def compute_all_metrics(self) -> Dict[str, Any]:
        """Compute all analytics metrics"""
        # Overall metrics
        overall = {
            'ctr': round(self.compute_ctr(), 2),
            'cpc': round(self.compute_cpc(), 2),
            'cpa': round(self.compute_cpa(), 2) if self.compute_cpa() is not None else None,
            'roas': round(self.compute_roas(), 2) if self.compute_roas() is not None else None,
            'total_spend': float(self.df['spend'].sum()),
            'total_revenue': float(self.df['revenue'].sum()) if 'revenue' in self.df.columns else None,
            'total_conversions': float(self.df['conversions'].sum()) if 'conversions' in self.df.columns else None,
        }

        # Metrics broken down by platform (e.g. Facebook, Google)
        platform_metrics: List[Dict[str, Any]] = []
        if 'platform' in self.df.columns:
            platform_grouped = self.df.groupby('platform').agg({
                'impressions': 'sum',
                'clicks': 'sum',
                'spend': 'sum',
                'conversions': 'sum' if 'conversions' in self.df.columns else 'sum',
                'revenue': 'sum' if 'revenue' in self.df.columns else 'sum',
            }).reset_index()

            def safe_ctr(row):
                return (row['clicks'] / row['impressions'] * 100) if row['impressions'] > 0 else 0.0

            def safe_cpc(row):
                return (row['spend'] / row['clicks']) if row['clicks'] > 0 else 0.0

            def safe_cpa(row):
                if 'conversions' not in platform_grouped.columns:
                    return None
                return (row['spend'] / row['conversions']) if row['conversions'] > 0 else None

            def safe_roas(row):
                if 'revenue' not in platform_grouped.columns:
                    return None
                return (row['revenue'] / row['spend']) if row['spend'] > 0 else None

            for _, row in platform_grouped.iterrows():
                record: Dict[str, Any] = {
                    'platform': row['platform'],
                    'total_spend': float(row['spend']),
                    'total_revenue': float(row['revenue']) if 'revenue' in platform_grouped.columns else None,
                    'total_conversions': float(row['conversions']) if 'conversions' in platform_grouped.columns else None,
                    'ctr': round(float(safe_ctr(row)), 2),
                    'cpc': round(float(safe_cpc(row)), 2),
                    'cpa': round(float(safe_cpa(row)), 2) if safe_cpa(row) is not None else None,
                    'roas': round(float(safe_roas(row)), 2) if safe_roas(row) is not None else None,
                }
                platform_metrics.append(record)

        return {
            'overall_metrics': overall,
            'platform_metrics': platform_metrics,
            'best_performing': self.get_best_performing_ads(),
            'worst_performing': self.get_worst_performing_ads(),
            'spend_inefficiencies': self.identify_spend_inefficiencies(),
            'trends': self.compute_trends()
        }

