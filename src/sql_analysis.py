import duckdb
from pathlib import Path

project_folder = Path(__file__).resolve().parent.parent

data_folder = (
    project_folder
    / "data"
    / "raw"
    / "aml_20k_combined"
)

nodes_path = str(data_folder / "nodes.csv")
transactions_path = str(data_folder / "transactions.csv")

connection = duckdb.connect()

# Create SQL views from CSV files
connection.execute(f"""
    CREATE VIEW nodes AS
    SELECT *
    FROM read_csv_auto('{nodes_path}')
""")

connection.execute(f"""
    CREATE VIEW transactions AS
    SELECT *
    FROM read_csv_auto('{transactions_path}')
""")

# =====================================
# QUERY 1: TOP ACCOUNTS BY OUTGOING AMOUNT
# =====================================

print("\n========== TOP OUTGOING ACCOUNTS ==========")

result = connection.execute("""
    SELECT
        sourceNodeId AS account_id,
        COUNT(*) AS transaction_count,
        ROUND(SUM(value), 2) AS total_outgoing
    FROM transactions
    GROUP BY sourceNodeId
    ORDER BY total_outgoing DESC
    LIMIT 10
""").fetchdf()

print(result)

# =====================================
# QUERY 2: TOP TRANSACTION ROUTES
# =====================================

print("\n========== TOP TRANSACTION ROUTES ==========")

result = connection.execute("""
    SELECT
        sourceNodeId AS sender,
        targetNodeId AS receiver,
        COUNT(*) AS transaction_count,
        ROUND(SUM(value), 2) AS total_value
    FROM transactions
    GROUP BY sourceNodeId, targetNodeId
    ORDER BY total_value DESC
    LIMIT 10
""").fetchdf()

print(result)

# =====================================
# QUERY 3: FRAUD-LABELED ACCOUNT ACTIVITY
# =====================================

print("\n========== FRAUD-LABELED ACCOUNT ACTIVITY ==========")

result = connection.execute("""
    SELECT
        n.isFraud,
        COUNT(DISTINCT n.nodeid) AS account_count,
        COUNT(t.sourceNodeId) AS transaction_count,
        ROUND(SUM(t.value), 2) AS total_transaction_value
    FROM nodes n
    LEFT JOIN transactions t
        ON n.nodeid = t.sourceNodeId
    GROUP BY n.isFraud
    ORDER BY n.isFraud
""").fetchdf()

print(result)

# =====================================
# QUERY 4: TRANSACTION ACTIVITY BY TIME
# =====================================

print("\n========== ACTIVITY BY TIME ==========")

result = connection.execute("""
    SELECT
        time,
        COUNT(*) AS transaction_count,
        ROUND(SUM(value), 2) AS total_value
    FROM transactions
    GROUP BY time
    ORDER BY time
    LIMIT 20
""").fetchdf()

print(result)

connection.close()

print("\nSQL analysis completed successfully.")