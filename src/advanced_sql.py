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
# QUERY 1: FRAUD-LABELED ACCOUNT RANKING
# =====================================

print("\n========== FRAUD-LABELED ACCOUNT RANKING ==========")

result = connection.execute("""
    SELECT
        t.sourceNodeId AS account_id,
        n.isFraud,
        COUNT(*) AS transaction_count,
        ROUND(SUM(t.value), 2) AS total_outgoing,

        RANK() OVER (
            ORDER BY SUM(t.value) DESC
        ) AS amount_rank

    FROM transactions t
    JOIN nodes n
        ON t.sourceNodeId = n.nodeid

    GROUP BY
        t.sourceNodeId,
        n.isFraud

    ORDER BY total_outgoing DESC
    LIMIT 20
""").fetchdf()

print(result)

# =====================================
# QUERY 2: HIGH-VALUE TRANSACTIONS
# =====================================

print("\n========== HIGH-VALUE TRANSACTIONS ==========")

result = connection.execute("""
    SELECT
        sourceNodeId AS sender,
        targetNodeId AS receiver,
        value,
        time,

        CASE
            WHEN value >= 500 THEN 'High'
            WHEN value >= 250 THEN 'Medium'
            ELSE 'Low'
        END AS transaction_category

    FROM transactions

    ORDER BY value DESC
    LIMIT 20
""").fetchdf()

print(result)

# =====================================
# QUERY 3: TIME-BASED TRANSACTION RANKING
# =====================================

print("\n========== TIME-BASED TRANSACTION RANKING ==========")

result = connection.execute("""
    SELECT
        time,
        COUNT(*) AS transaction_count,
        ROUND(SUM(value), 2) AS total_value,

        RANK() OVER (
            ORDER BY SUM(value) DESC
        ) AS value_rank

    FROM transactions

    GROUP BY time
    ORDER BY value_rank
    LIMIT 20
""").fetchdf()

print(result)

# =====================================
# QUERY 4: ACCOUNTS CONNECTED TO FRAUD LABELS
# =====================================

print("\n========== FRAUD-CONNECTED ACCOUNTS ==========")

result = connection.execute("""
    SELECT
        t.sourceNodeId AS sender,
        COUNT(*) AS transaction_count,
        ROUND(SUM(t.value), 2) AS total_value

    FROM transactions t

    JOIN nodes n
        ON t.targetNodeId = n.nodeid

    WHERE n.isFraud = 1

    GROUP BY t.sourceNodeId
    ORDER BY total_value DESC
    LIMIT 20
""").fetchdf()

print(result)

connection.close()

print("\nAdvanced SQL analysis completed successfully.")