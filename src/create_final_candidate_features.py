from pathlib import Path
import pandas as pd


# --------------------------------------------------
# 1. Set project paths
# --------------------------------------------------

PROJECT_FOLDER = Path(__file__).resolve().parent.parent

OUTPUT_FOLDER = PROJECT_FOLDER / "outputs"

MEMBERSHIP_FILE = (
    OUTPUT_FOLDER / "ring_candidate_membership.csv"
)

TRANSACTIONS_FILE = (
    PROJECT_FOLDER
    / "data"
    / "raw"
    / "aml_20k_combined"
    / "transactions.csv"
)

NODES_FILE = (
    PROJECT_FOLDER
    / "data"
    / "raw"
    / "aml_20k_combined"
    / "nodes.csv"
)


# --------------------------------------------------
# 2. Load datasets
# --------------------------------------------------

membership = pd.read_csv(MEMBERSHIP_FILE)

transactions = pd.read_csv(TRANSACTIONS_FILE)

nodes = pd.read_csv(NODES_FILE)

print("All datasets loaded successfully.")


# --------------------------------------------------
# 3. Prepare account and fraud-label data
# --------------------------------------------------

nodes["nodeid"] = nodes["nodeid"].astype(int)

fraud_labels = dict(
    zip(
        nodes["nodeid"],
        nodes["isFraud"]
    )
)


# --------------------------------------------------
# 4. Create candidate account sets
# --------------------------------------------------

account_columns = [
    "account_1",
    "account_2",
    "account_3"
]

candidate_accounts = {}

candidate_cycles = {}

for candidate_id, group in membership.groupby(
    "candidate_id"
):

    accounts = set()

    for column in account_columns:

        accounts.update(
            group[column].astype(int)
        )

    candidate_accounts[candidate_id] = accounts

    candidate_cycles[candidate_id] = len(group)


# --------------------------------------------------
# 5. Prepare transaction data
# --------------------------------------------------

transactions["sourceNodeId"] = (
    transactions["sourceNodeId"].astype(int)
)

transactions["targetNodeId"] = (
    transactions["targetNodeId"].astype(int)
)

transactions["value"] = (
    transactions["value"].astype(float)
)


# --------------------------------------------------
# 6. Calculate candidate-level features
# --------------------------------------------------

results = []


for candidate_id, accounts in candidate_accounts.items():

    cycle_count = candidate_cycles[candidate_id]

    account_count = len(accounts)

    # ----------------------------------------------
    # Fraud-label information
    # ----------------------------------------------

    fraud_label_count = sum(
        fraud_labels.get(account, 0)
        for account in accounts
    )

    fraud_label_rate = (
        fraud_label_count
        / account_count
        * 100
        if account_count > 0
        else 0
    )


    # ----------------------------------------------
    # Internal transactions
    # ----------------------------------------------

    internal_transactions = transactions[
        transactions["sourceNodeId"].isin(accounts)
        &
        transactions["targetNodeId"].isin(accounts)
    ]

    internal_count = len(
        internal_transactions
    )

    internal_value = internal_transactions[
        "value"
    ].sum()


    # ----------------------------------------------
    # Incoming transactions
    # ----------------------------------------------

    incoming_transactions = transactions[
        transactions["targetNodeId"].isin(accounts)
    ]

    incoming_value = incoming_transactions[
        "value"
    ].sum()


    # ----------------------------------------------
    # Outgoing transactions
    # ----------------------------------------------

    outgoing_transactions = transactions[
        transactions["sourceNodeId"].isin(accounts)
    ]

    outgoing_value = outgoing_transactions[
        "value"
    ].sum()


    # ----------------------------------------------
    # Corrected internal value ratio
    # ----------------------------------------------

    # All transactions involving the candidate group.
    # Each transaction is counted only once.

    involved_transactions = transactions[
        transactions["sourceNodeId"].isin(accounts)
        |
        transactions["targetNodeId"].isin(accounts)
    ]

    total_involved_value = involved_transactions[
        "value"
    ].sum()

    internal_value_ratio = (
        internal_value
        / total_involved_value
        * 100
        if total_involved_value > 0
        else 0
    )


    # ----------------------------------------------
    # Account participation analysis
    # ----------------------------------------------

    account_participation = {}

    candidate_membership = membership[
        membership["candidate_id"] == candidate_id
    ]

    for _, cycle in candidate_membership.iterrows():

        cycle_accounts = set(
            int(cycle[column])
            for column in account_columns
        )

        for account in cycle_accounts:

            account_participation[account] = (
                account_participation.get(account, 0)
                + 1
            )


    # ----------------------------------------------
    # Repeated-account features
    # ----------------------------------------------

    repeated_accounts = sum(
        count > 1
        for count in account_participation.values()
    )

    highest_participation = max(
        account_participation.values()
    )


    if cycle_count > 1:

        repeated_account_ratio = (
            repeated_accounts
            / account_count
            * 100
        )

        participation_share = (
            highest_participation
            / cycle_count
            * 100
        )

    else:

        repeated_account_ratio = None

        participation_share = None


    # ----------------------------------------------
    # Store candidate features
    # ----------------------------------------------

    results.append({

        "candidate_id": candidate_id,

        "account_count": account_count,

        "cycle_count": cycle_count,

        "internal_transaction_count": (
            internal_count
        ),

        "internal_transaction_value": round(
            internal_value,
            2
        ),

        "incoming_transaction_value": round(
            incoming_value,
            2
        ),

        "outgoing_transaction_value": round(
            outgoing_value,
            2
        ),

        "internal_value_ratio": round(
            internal_value_ratio,
            2
        ),

        "repeated_account_count": (
            repeated_accounts
        ),

        "repeated_account_ratio": (
            round(
                repeated_account_ratio,
                2
            )
            if repeated_account_ratio is not None
            else None
        ),

        "highest_account_participation": (
            highest_participation
        ),

        "highest_participation_share": (
            round(
                participation_share,
                2
            )
            if participation_share is not None
            else None
        ),

        "fraud_label_count": (
            fraud_label_count
        ),

        "fraud_label_rate": round(
            fraud_label_rate,
            2
        )

    })


# --------------------------------------------------
# 7. Create final feature table
# --------------------------------------------------

final_features = pd.DataFrame(results)


# --------------------------------------------------
# 8. Save output file
# --------------------------------------------------

output_file = (
    OUTPUT_FOLDER
    / "final_candidate_features.csv"
)

final_features.to_csv(
    output_file,
    index=False
)


# --------------------------------------------------
# 9. Display results
# --------------------------------------------------

print("\nFinal candidate feature table created.")

print(
    "Total candidates:",
    len(final_features)
)

print("\nPreview:")

print(
    final_features.head(10).to_string(
        index=False
    )
)

print("\nSaved file:")

print(output_file)