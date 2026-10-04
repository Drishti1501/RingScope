import pandas as pd
from pathlib import Path


# ===================================
# 1. Set project root folder
# ===================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUTPUTS_FOLDER = PROJECT_ROOT / "outputs"
DATA_FOLDER = PROJECT_ROOT / "data" / "raw" / "aml_20k_combined"


# ===================================
# 2. Load data
# ===================================

print("Loading data...")

membership_path = OUTPUTS_FOLDER / "ring_candidate_membership.csv"
transactions_path = DATA_FOLDER / "transactions.csv"
nodes_path = DATA_FOLDER / "nodes.csv"

membership = pd.read_csv(membership_path)

transactions = pd.read_csv(transactions_path)

nodes = pd.read_csv(nodes_path)

print(f"Membership records: {len(membership)}")
print(f"Transactions loaded: {len(transactions)}")


# ===================================
# 3. Create fraud label lookup
# ===================================

print("Creating fraud label lookup...")

fraud_labels = dict(
    zip(
        nodes["nodeid"],
        nodes["isFraud"]
    )
)


# ===================================
# 4. Analyze candidate groups
# ===================================

print("Analyzing candidate groups...")

results = []

for candidate_id, group_data in membership.groupby(
    "candidate_id"
):

    # Collect accounts in this candidate group
    accounts = set()

    for _, row in group_data.iterrows():

        accounts.update([
            int(row["account_1"]),
            int(row["account_2"]),
            int(row["account_3"])
        ])

    # Select internal transactions
    internal_transactions = transactions[
        transactions["sourceNodeId"].isin(accounts)
        &
        transactions["targetNodeId"].isin(accounts)
    ]

    # Count fraud-labeled accounts
    fraud_account_count = sum(
        fraud_labels.get(account_id, 0) == 1
        for account_id in accounts
    )

    # Calculate outgoing transaction value
    outgoing_amount = transactions[
        transactions["sourceNodeId"].isin(accounts)
    ]["value"].sum()

    # Calculate incoming transaction value
    incoming_amount = transactions[
        transactions["targetNodeId"].isin(accounts)
    ]["value"].sum()

    # Store group-level features
    results.append({

        "candidate_id": candidate_id,

        "account_count": len(accounts),

        "cycle_count": len(group_data),

        "internal_transaction_count": len(
            internal_transactions
        ),

        "internal_transaction_value": round(
            internal_transactions["value"].sum(),
            2
        ),

        "total_outgoing_value": round(
            outgoing_amount,
            2
        ),

        "total_incoming_value": round(
            incoming_amount,
            2
        ),

        "fraud_account_count": fraud_account_count,

        "fraud_rate": round(
            fraud_account_count / len(accounts) * 100,
            2
        )

    })


# ===================================
# 5. Create analysis DataFrame
# ===================================

candidate_analysis = pd.DataFrame(results)


# ===================================
# 6. Classify candidate groups
# ===================================

def classify_candidate(row):

    if row["cycle_count"] == 1:

        return "Single-cycle candidate"

    elif row["cycle_count"] <= 5:

        return "Small multi-cycle candidate"

    else:

        return "Large multi-cycle candidate"


candidate_analysis["candidate_category"] = (
    candidate_analysis.apply(
        classify_candidate,
        axis=1
    )
)


# ===================================
# 7. Sort results
# ===================================

candidate_analysis = candidate_analysis.sort_values(
    by=[
        "cycle_count",
        "internal_transaction_value"
    ],
    ascending=False
)


# ===================================
# 8. Save results
# ===================================

output_path = (
    OUTPUTS_FOLDER /
    "candidate_investigation_analysis.csv"
)

candidate_analysis.to_csv(
    output_path,
    index=False
)


# ===================================
# 9. Display results
# ===================================

print("\nCandidate Analysis Summary")
print("-" * 60)

print(
    candidate_analysis
    .head(20)
    .to_string(index=False)
)

print("\nCandidate category distribution:")

print(
    candidate_analysis["candidate_category"]
    .value_counts()
)

print("\nAnalysis saved to:")

print(output_path)