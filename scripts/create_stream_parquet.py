import pandas as pd
from datetime import datetime, timedelta
import os

# Create sample data with the correct schema
data = {
    'driver_id': ['1', '2', '3'],
    'conv_percentage': [75.5, 82.3, 68.9],
    'acc_percentage': [92.1, 88.7, 95.4],
    'event_timestamp': [datetime.now() - timedelta(hours=i) for i in range(3)],
    'created': [datetime.now() - timedelta(hours=i) for i in range(3)]
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to parquet in the data folder
df.to_parquet('../my_project/feature_repo/data/driver_stats_stream2.parquet') 