import pandas as pd

# The default location for the quickstart parquet file
parquet_file_path = "./data/driver_stats.parquet"

try:
    df = pd.read_parquet(parquet_file_path)
    print(df.head()) # Print the first 5 rows
    print(df.info()) # Print a summary of the DataFrame (columns, types, non-null values)
except FileNotFoundError:
    print(f"Error: The file '{parquet_file_path}' was not found. Make sure you are in the 'my_project/feature_repo' directory.")
except Exception as e:
    print(f"An error occurred: {e}") 