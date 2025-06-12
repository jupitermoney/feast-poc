# Feast Quickstart Guide

This `README.md` provides a step-by-step guide to setting up and running a local Feast project, based on the Feast quickstart. It covers setting up a virtual environment, installing Feast, initializing a project, inspecting sample data, and understanding the local Feast stores.

## 1. Setup Python Virtual Environment

It's highly recommended to use a virtual environment to manage dependencies for your Feast project. This isolates your project's dependencies from your system-wide Python installation.

```bash
python -m venv venv/
source venv/bin/activate
```

## 2. Install Feast and Dependencies

Once your virtual environment is active, upgrade `pip` and then install the `feast`, `pandas`, and `pyarrow` libraries.

```bash
python3 -m pip install --upgrade pip
pip install feast pandas pyarrow
```

## 3. Initialize a Feast Project

Initialize a new Feast project. This will create a sample feature repository with example feature definitions and an offline data source.

```bash
feast init my_project
```

Navigate into your newly created project directory:

```bash
cd my_project
```

## 4. Inspect Offline Store Data

The quickstart project comes with a sample Parquet file (`driver_stats.parquet`) that serves as the offline feature store. You can inspect its contents using a Python script.

First, navigate into the `feature_repo` directory:

```bash
cd feature_repo
```

Then, you can run the `inspect_data.py` script located within this directory. This script reads the Parquet file and prints the first few rows and a summary of its structure.

```bash
python inspect_data.py
```

**Expected Output (example):**

```
  event_timestamp  driver_id  conv_rate  acc_rate  avg_daily_trips                 created
0 2025-05-28 10:00:00+00:00       1005   0.482020  0.025346              407 2025-06-12 10:57:04.001
1 2025-05-28 11:00:00+00:00       1005   0.891229  0.104370              892 2025-06-12 10:57:04.001
2 2025-05-28 12:00:00+00:00       1005   0.670584  0.815993              216 2025-06-12 10:57:04.001
3 2025-05-28 13:00:00+00:00       1005   0.273240  0.316864              338 2025-06-12 10:57:04.001
4 2025-05-28 14:00:00+00:00       1005   0.763663  0.999113              656 2025-06-12 10:57:04.001
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 1807 entries, 0 to 1806
Data columns (total 6 columns):
 #   Column           Non-Null Count  Dtype
---  ------           --------------  -----
 0   event_timestamp  1807 non-null   datetime64[ns, UTC]
 1   driver_id        1807 non-null   int64
 2   conv_rate        1807 non-null   float32
 3   acc_rate         1807 non-null   float32
 4   avg_daily_trips  1807 non-null   int32
 5   created          1807 non-null   datetime64[us]
dtypes: datetime64[ns, UTC](1), datetime64[us](1), float32(2), int32(1), int64(1)
memory usage: 63.7 KB
None
```

## 5. Run the Feast Quickstart Workflow

After inspecting the data, you can run the Feast quickstart workflow, which applies the feature definitions and materializes data into the online store.

Make sure you are in the `my_project/feature_repo` directory, then run:

```bash
python test_workflow.py
```

**Expected Output (example):**

```
Created project my_project
Created entity driver
Created feature view driver_hourly_stats
Created feature view driver_hourly_stats_fresh
Created on demand feature view transformed_conv_rate_fresh
Created on demand feature view transformed_conv_rate
Created feature service driver_activity_v3
Created feature service driver_activity_v2
Created feature service driver_activity_v1

Created sqlite table my_project_driver_hourly_stats_fresh
Created sqlite table my_project_driver_hourly_stats


upon subsequent runs if there are no changes in feature_store.yaml
No changes to registry
No changes to infrastructure
```

## 6. Understanding Feast Local Stores

When `feast apply` (which `test_workflow.py` executes implicitly) runs successfully, it creates two important local database files:

*   **`online_store.db`**: This is your Feast Online Store. For the quickstart, Feast uses a SQLite database as a simple, local online store. Its purpose is to store the latest feature values for quick retrieval during online inference.

*   **`registry.db`**: This is your Feast Registry. It's a SQLite database file that stores all the metadata about your Feast project. This includes definitions of your entities, feature views, data sources, and other configurations you define in your `.py` files within the `feature_repo` directory. Think of it as the "brain" of your Feast feature store, keeping track of everything you've "applied."

You can inspect these SQLite databases using a command-line tool like `sqlite3` (e.g., `sqlite3 registry.db`) or via Python's `sqlite3` module.

SQLite commands
- .tables
- .schema <table_name>
- SELECT * FROM <table_name> LIMIT 5;
- .quit


sqlite3 online_store.db


sqlite> .tables
my_project_driver_hourly_stats        my_project_driver_hourly_stats_fresh
sqlite> .schema my_project_driver_hourly_stats
CREATE TABLE my_project_driver_hourly_stats (
                entity_key BLOB,
                feature_name TEXT,
                value BLOB,
                vector_value BLOB,
                event_ts timestamp,
                created_ts timestamp,
                PRIMARY KEY(entity_key, feature_name)
            );
CREATE INDEX my_project_driver_hourly_stats_ek ON my_project_driver_hourly_stats (entity_key);


.schema my_project_driver_hourly_stats_fresh.schema my_project_driver_hourly_stats_fresh
CREATE TABLE my_project_driver_hourly_stats_fresh (
                entity_key BLOB,
                feature_name TEXT,
                value BLOB,
                vector_value BLOB,
                event_ts timestamp,
                created_ts timestamp,
                PRIMARY KEY(entity_key, feature_name)
            );
CREATE INDEX my_project_driver_hourly_stats_fresh_ek ON my_project_driver_hourly_stats_fresh (entity_key);
sqlite>