"""
Script to transform marketing_and_product_performance.csv to work with Ad Performance Engine
This script:
1. Renames columns to match our expected format
2. Adds a date column (synthetic, based on row order)
3. Adds impressions column (estimated from clicks and CTR)
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Read the original dataset
df = pd.read_csv('marketing_and_product_performance.csv')

print(f"Original dataset shape: {df.shape}")
print(f"Original columns: {list(df.columns)}")

# Create a copy for transformation
df_transformed = df.copy()

# 1. Rename columns to match our expected format
column_mapping = {
    'Campaign_ID': 'campaign_name',
    'Budget': 'spend',
    'Clicks': 'clicks',
    'Conversions': 'conversions',
    'Revenue_Generated': 'revenue'
}

df_transformed = df_transformed.rename(columns=column_mapping)

# 2. Add date column - create a time series starting from 30 days ago
# We'll distribute the rows across the last 30 days
start_date = datetime.now() - timedelta(days=30)
df_transformed['date'] = pd.date_range(start=start_date, periods=len(df_transformed), freq='D')[:len(df_transformed)]

# If we have more rows than days, repeat dates
if len(df_transformed) > 30:
    days_needed = len(df_transformed)
    date_list = []
    for i in range(days_needed):
        date_list.append(start_date + timedelta(days=i % 30))
    df_transformed['date'] = date_list

# 3. Add impressions column
# Estimate impressions based on clicks and a realistic CTR (typically 1-3%)
# Formula: impressions = clicks / CTR
# We'll use a random CTR between 0.5% and 3% for each row
np.random.seed(42)  # For reproducibility
ctr_values = np.random.uniform(0.005, 0.03, len(df_transformed))
df_transformed['impressions'] = (df_transformed['clicks'] / ctr_values).astype(int)

# Ensure impressions is at least equal to clicks
df_transformed['impressions'] = df_transformed[['impressions', 'clicks']].max(axis=1)

# 4. Add platform column (optional but nice to have)
# Randomly assign platforms
platforms = ['Facebook', 'Google', 'Instagram', 'LinkedIn', 'Twitter']
df_transformed['platform'] = np.random.choice(platforms, size=len(df_transformed))

# 5. Select only the columns we need
required_columns = ['date', 'platform', 'campaign_name', 'impressions', 'clicks', 'spend']
optional_columns = ['conversions', 'revenue']

final_columns = required_columns.copy()
for col in optional_columns:
    if col in df_transformed.columns:
        final_columns.append(col)

df_final = df_transformed[final_columns].copy()

# 6. Sort by date
df_final = df_final.sort_values('date').reset_index(drop=True)

# 7. Format date as YYYY-MM-DD
df_final['date'] = df_final['date'].dt.strftime('%Y-%m-%d')

# 8. Save the transformed dataset
output_file = 'marketing_data_transformed.csv'
df_final.to_csv(output_file, index=False)

print(f"\n✅ Transformation complete!")
print(f"Transformed dataset shape: {df_final.shape}")
print(f"Columns: {list(df_final.columns)}")
print(f"Date range: {df_final['date'].min()} to {df_final['date'].max()}")
print(f"\nSaved to: {output_file}")
print(f"\nFirst few rows:")
print(df_final.head())

