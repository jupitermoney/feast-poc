import pandas as pd

# The default location for the quickstart parquet file
parquet_file_path = "data/driver_stats.parquet"

print("=== Loading driver_stats.parquet and filtering for driver_id 1004 ===")

try:
    # Load the full DataFrame into memory
    print("Loading full parquet file...")
    df = pd.read_parquet(parquet_file_path)
    
    print(f"Total rows loaded: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    print("\nFirst 5 rows of full dataset:")
    print(df.head())
    
    # Filter for driver_id 1004
    print(f"\n=== Filtering for driver_id 1004 ===")
    driver_1004_data = df[df['driver_id'] == 1004]
    print(f"Found {len(driver_1004_data)} rows for driver_id 1004:")
    print(driver_1004_data)
    
    # Get the latest row for driver_id 1004 (ordered by timestamp desc, limit 1)
    if len(driver_1004_data) > 0:
        print(f"\n=== Latest row for driver_id 1004 (ORDER BY timestamp DESC LIMIT 1) ===")
        
        # Find the timestamp column (could be 'createdat', 'created_at', 'event_timestamp', etc.)
        timestamp_cols = [col for col in driver_1004_data.columns if 'time' in col.lower() or 'date' in col.lower() or 'created' in col.lower()]
        
        if timestamp_cols:
            timestamp_col = timestamp_cols[0]  # Use the first timestamp column found
            print(f"Using timestamp column: {timestamp_col}")
            
            # Sort by timestamp descending and get the first row (latest)
            latest_row = driver_1004_data.sort_values(timestamp_col, ascending=False).iloc[0]
            print("Latest row:")
            print(latest_row)
        else:
            print("No timestamp column found. Available columns:")
            print(list(driver_1004_data.columns))
            print("Getting the last row by index instead:")
            latest_row = driver_1004_data.iloc[-1]
            print(latest_row)
        
        print(f"\n=== Summary statistics for all driver_id 1004 rows ===")
        print(driver_1004_data.describe())
        
except FileNotFoundError:
    print(f"Error: The file '{parquet_file_path}' was not found.")
except Exception as e:
    print(f"An error occurred: {e}")