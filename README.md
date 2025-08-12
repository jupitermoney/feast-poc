# Feast Quickstart Guide

This `README.md` provides a step-by-step guide to setting up and running a local Feast project, based on the Feast quickstart. It covers setting up a virtual environment, installing Feast, initializing a project, inspecting sample data, and understanding the local Feast stores.

## Concepts

Repository
Feast users use Feast to manage two important sets of configuration:
- Configuration about how to run Feast on your infrastructure: A feature_store.yaml file containing infrastructural configuration. 
- Feature definitions: A collection of Python files containing feature declarations. Feast reads all Python files recursively when feast apply is ran, including subdirectories, even if they don't contain feature definitions.

Data sources
TODO

Offline stores
TODO

Online stores
Supports PSQL, redis, Cassandra, ScyllaDB, etc

Registry
The Feast feature registry is a central catalog of all feature definitions and their related metadata. Feast uses the registry to store all applied Feast objects (e.g. Feature views, entities, etc).
Supports S3 and SQL as regsitries,

Feature server
It is a REST API server built using FastAPI and exposes a limited set of endpoints to serve features, push data, and support materialization operations. The server is scalable, flexible, and designed to work seamlessly with various deployment environments, including local setups and cloud-based systems.

The Feature Server operates as a stateless service backed by two key components:
- Online Store: The primary data store used for low-latency feature retrieval.
- Registry: The metadata store that defines feature sets, feature views, and their relationships to entities.

Endpoints Overview
- /get-online-features: Retrieves feature values for specified entities and feature references.
- /push: Pushes feature data to the online and/or offline store.

- /materialize: Materializes features within a specific time range to the online store.
- /materialize-incremental: Incrementally materializes features up to the current timestamp.
- /retrieve-online-documents: Supports Vector Similarity Search for RAG (Alpha end-ponit)
- /docs: API Contract for available endpoints


Following are the kind of servers
- Feature server 
- Registry server: https://github.com/feast-dev/feast/blob/v0.49-branch/docs/reference/registry/registry-permissions.md
- Offline server


## Quick links
- CLI commands: https://docs.feast.dev/reference/feast-cli-commands or typing feast on terminal. 
- Productionising feast: https://docs.feast.dev/how-to-guides/running-feast-in-production#42-deploy-feast-feature-servers-on-kubernetes
- Feature server: https://github.com/feast-dev/feast/tree/v0.49-branch/docs/reference/feature-servers

## 1. Setup Python Virtual Environment

It's highly recommended to use a virtual environment to manage dependencies for your Feast project. This isolates your project's dependencies from your system-wide Python installation.

```bash
python -m venv venv/
source venv/bin/activate
cd my_project/feature_repo
```

## 2. Install Feast and Dependencies

Once your virtual environment is active, upgrade `pip` and then install the core `feast`, `pandas`, and `pyarrow` libraries. If you plan to use specific online stores like PostgreSQL or Redis, install their respective Feast extensions.

```bash
python3 -m pip install --upgrade pip
pip install feast pandas pyarrow
# Optional: Install for PostgreSQL online store
pip install \'feast[postgres]\'
# Optional: Install for Redis online store
# pip install \'feast[redis]\'
# Optional: Install for Delta Lake support (if needed for offline store)
pip install deltalake==0.25.4
# Optional: Install PySpark (if using Spark with Delta Lake)
pip install pyspark

pip uninstall protobuf -y && pip install protobuf==5.29.3

```

## 3. Initialize a Feast Project

Initialize a new Feast project. This will create a sample feature repository with example feature definitions and an offline data source.

```bash
feast init my_project
```

Navigate into your newly created project's feature repository directory:

```bash
cd my_project/feature_repo
```

## 4. Inspect Offline Store Data

The quickstart project comes with sample data. We've updated the `inspect_data.py` script to read both the `driver_stats.parquet` file and the `sms` Delta table.

Run the `inspect_data.py` script located within this directory. This script reads the data sources and prints the first few rows and a summary of their structure.

```bash
python inspect_data.py
```

**Expected Output:**
You should see output similar to the following, showing data from both the Parquet file and the Delta table, along with their respective schemas. The exact content will depend on your data.

```
--- Driver Stats Data ---
  event_timestamp  driver_id  conv_rate  acc_rate  avg_daily_trips                 created
0 2025-05-28 10:00:00+00:00       1005   0.482020  0.025346              407 2025-06-12 10:57:04.001
... (truncated for brevity)
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 1807 entries, 0 to 1806
Data columns (total 6 columns):
 #   Column           Non-Null Count  Dtype
---  ------           --------------  -----
... (truncated for brevity)
--- SMS Delta Table Data (using Spark) ---
+-----------+---------+-------------------+-------+----------+--------+------------------+---------------------+...
|customer_id|sender_id|  message_timestamp|concept|request_id|sms_type|transaction_type|transaction_ner_account|...
+-----------+---------+-------------------+-------+----------+--------+------------------+-----------------------+...
|       null|   AIRTEL|2015-01-02 13:38:24|  Bank |      null|     1.0|              null|                   null|...
... (truncated for brevity)
root
 |-- customer_id: string (nullable = true)
 |-- sender_id: string (nullable = true)\
 |-- message_timestamp: timestamp (nullable = true)
... (truncated for brevity)
```

## 5. Run the Feast Quickstart Workflow

After inspecting the data, you can run the Feast quickstart workflow, which applies the feature definitions and materializes data into the online store.

Make sure you are in the `my_project/feature_repo` directory, then run:

```bash
python test_workflow.py
```

**Expected Output:**
You should see output indicating that Feast is creating your project, entities, feature views, and feature services, and then materializing data into the online store.

```
Created project my_project
Created entity driver
Created feature view driver_hourly_stats
... (truncated for brevity)
```

## 6. Understanding Feast Local Stores

When `feast apply` (which `test_workflow.py` executes implicitly) runs successfully, it creates two important local database files in your `my_project/feature_repo` directory:

*   **`online_store.db`**: This is your Feast Online Store. For the quickstart, Feast uses a SQLite database as a simple, local online store. Its purpose is to store the latest feature values for quick retrieval during online inference.
*   **`registry.db`**: This is your Feast Registry. It's a SQLite database file that stores all the metadata about your Feast project. This includes definitions of your entities, feature views, data sources, and other configurations you define in your `.py` files within the `feature_repo` directory. Think of it as the "brain" of your Feast feature store, keeping track of everything you've "applied."

### Inspecting SQLite Databases

You can inspect these SQLite databases using a command-line tool like `sqlite3`.

First, navigate to the `my_project/feature_repo` directory.

```bash
cd my_project/feature_repo
```

Then, you can open a database (e.g., `registry.db` or `online_store.db`) and use standard SQLite commands:

```bash
sqlite3 registry.db
```

Within the `sqlite3` prompt, you can use commands like:

*   `.tables`: List all tables in the database.
*   `.schema <table_name>`: Display the schema for a specific table.
*   `SELECT * FROM <table_name> LIMIT 5;`: View the first 5 rows of a table.
*   `.quit`: Exit the `sqlite3` prompt.

For `online_store.db`, you will typically see tables corresponding to your feature views, like `my_project_driver_hourly_stats`. These tables store your materialized feature data.

### Feast Online Store Data Structure (General)

Regardless of the specific online store (SQLite, PostgreSQL, Redis, etc.), Feast generally stores feature data in a key-value like structure.

*   **Feature Views as Tables/Collections:** Each feature view you define in Feast (`.py` files) usually corresponds to a table (in relational databases like SQLite/PostgreSQL) or a collection/hash (in NoSQL stores like Redis).
*   **Entity Keys:** Data is typically indexed by the entity key (e.g., `driver_id`).
*   **Feature Values:** Individual features for an entity are stored as values. In some online stores, Feast might serialize features (e.g., using Protocol Buffers) into binary formats for efficiency, meaning you might not be able to directly query human-readable values via standard SQL tools without deserialization.

**Example (Conceptual):**

*   **PostgreSQL:** Feature views appear as tables. Each row in a feature view table would represent a set of features for a specific entity, with `entity_key` and `feature_name` often forming part of the primary key. Values are often stored as `bytea` (binary data) for efficiency.
*   **Redis:** Feature data is stored as key-value pairs, where the key might be a combination of the project, entity ID, and feature view name, and the value is the serialized feature data.

### Understanding the Delta Table Structure

The `sms` directory itself represents the entire Delta table. It's not just a regular folder with files; it's a **versioned** and **transactional** table adhering to the Delta Lake open-source storage format. All data files and the transaction log for this table reside within this directory.

*   **`_delta_log/` (The Transaction Log):**
    This is the core component that provides all of Delta Lake's powerful features.
    *   **ACID Properties:** It contains a series of JSON files (e.g., `00000000000000000000.json`) that record every change made to the Delta table as a transaction. This log ensures Atomicity, Consistency, Isolation, and Durability (ACID) properties.
    *   **Metadata:** Each JSON file records metadata about operations (like `WRITE`, `DELETE`, `UPDATE`), the schema at that point, files added/removed, and configuration settings (e.g., `delta.enableDeletionVectors`).
    *   **Schema Evolution:** Changes to the table schema (e.g., adding/dropping columns) are recorded here, allowing graceful schema evolution without rewriting all existing data files.
    *   **Time Travel:** The transaction log enables "time travel" to any previous state of the table using a timestamp or version number, which is powerful for auditing, debugging, or reproducing historical data.
    *   **Deletion Vectors:** These are managed and referenced within the `_delta_log`, optimizing delete/update operations by marking rows for deletion without immediate physical rewrites.

*   **`part-*.snappy.parquet` (The Data Files):**
    These are the actual data files of your Delta table.
    *   **Data Storage:** Delta Lake stores data in the [Apache Parquet format](https://parquet.apache.org/). Parquet is a highly efficient, open-source **columnar storage format**.
    *   **Columnar Format:** Data is stored column by column, which is highly beneficial for analytical queries as you only read the columns you need, leading to significant I/O performance improvements.
    *   **Compression (`.snappy`):** The `.snappy` extension indicates that these Parquet files are compressed using the Snappy compression algorithm, which reduces storage size and speeds up data transfer.

The `_delta_log` acts as the single source of truth, guiding compatible engines on which `.parquet` files form the current table version, its schema, and transaction history. This separation of metadata from data is a core principle enabling Delta Lake's benefits.
