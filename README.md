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
pip install 'feast[postgres]' # for python online store
pip install 'feast[redis]' # for redis
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


Choice of online store

PSQL
```
CREATE TABLE public.my_project_driver_hourly_stats (
	entity_key bytea NOT NULL,
	feature_name text NOT NULL,
	value bytea NULL,
	value_text text NULL,
	vector_value bytea NULL,
	event_ts timestamptz NULL,
	created_ts timestamptz NULL,
	CONSTRAINT my_project_driver_hourly_stats_pkey PRIMARY KEY (entity_key, feature_name)
);
CREATE INDEX my_project_driver_hourly_stats_ek ON public.my_project_driver_hourly_stats USING btree (entity_key);
```

- Each feature view is one table
- All features residing in one feature view exsits in one table
- Each feature for a key is one row

How does the data look like?
INSERT INTO my_project_driver_hourly_stats (entity_key,feature_name,value,value_text,vector_value,event_ts,created_ts) VALUES
	 (decode('020000006472697665725F69640400000004000000EC030000','hex'),'conv_rate',decode('3513F3423F','hex'),NULL,NULL,'2025-06-12 14:30:00.000','2025-06-12 16:27:04.001');
   
Basically, each feature got stored as a row in PSQL with primary key as (entity_key, feature_name) and indexed on entity_key. Protobuf-encoded binary format is the data in each, so cannot query directly from DB via SQL



Redis

docker run --name feast-redis -p 6379:6379 -d redis:latest

keys *
1) "\x02\x00\x00\x00driver_id\x04\x00\x00\x00\x04\x00\x00\x00\xed\x03\x00\x00my_project"
2) "\x02\x00\x00\x00driver_id\x04\x00\x00\x00\x04\x00\x00\x00\xe9\x03\x00\x00my_project"
3) "\x02\x00\x00\x00driver_id\x04\x00\x00\x00\x04\x00\x00\x00\xec\x03\x00\x00my_project"
4) "\x02\x00\x00\x00driver_id\x04\x00\x00\x00\x04\x00\x00\x00\xea\x03\x00\x00my_project"
5) "\x02\x00\x00\x00driver_id\x04\x00\x00\x00\x04\x00\x00\x00\xeb\x03\x00\x00my_project"
127.0.0.1:6379> get \x02\x00\x00\x00driver_id\x04\x00\x00\x00\x04\x00\x00\x00\xed\x03\x00\x00my_project
(nil)

 HGETALL "\x02\x00\x00\x00driver_id\x04\x00\x00\x00\x04\x00\x00\x00\xed\x03\x00\x00my_project"
 1) "_ts:driver_hourly_stats"
 2) "\b\x90\xae\xaa\xc2\x06"
 3) "a`\xe3\xda"
 4) "5\x96FV?"
 5) "\xfa^X\xad"
 6) "5d8S?"
 7) "\x18\xa5\xe5\xa3"
 8) " \xf0\x02"
 9) "_ts:driver_hourly_stats_fresh"
10) "\b\x90\xae\xaa\xc2\x06"
11) "\x03\xed\x10F"
12) "5\x96FV?"
13) "\xe2s\x86\xb9"
14) "5d8S?"
15) "?\te\xd3"
16) " \xf0\x02"

HGET "\x02\x00\x00\x00driver_id\x04\x00\x00\x00\x04\x00\x00\x00\xed\x03\x00\x00my_project" "_ts:driver_hourly_stats"
"a\xe3\xda" (likely driver_hourly_stats:conv_rate) and "5\x96FV?": 
* This is the field name (e.g., conv_rate for driver_hourly_stats). 
* This is the binary, Protobuf-encoded value for conv_rate

Basically it looks key_set is first level datastructure
both features have same keyset, so hash will be same
hash_key  = function(keyset)

inside the hashset, there will be fields, which are dependant on feature_view and feature name
field = function(feature_view, feature_name)

