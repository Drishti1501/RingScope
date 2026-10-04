from pathlib import Path
import pandas as pd
from collections import Counter


# --------------------------------------------------
# 1. Set project paths
# --------------------------------------------------

PROJECT_FOLDER = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_FOLDER
    / "outputs"
    / "ring_candidate_membership.csv"
)

OUTPUT_FOLDER = PROJECT_FOLDER / "outputs"


# --------------------------------------------------
# 2. Load candidate membership data
# --------------------------------------------------

membership_data = pd.read_csv(INPUT_FILE)

print("Membership data loaded successfully.")
print("Total rows:", len(membership_data))


# --------------------------------------------------
# 3. Identify account columns
# --------------------------------------------------

account_columns = [
    "account_1",
    "account_2",
    "account_3"
]


# --------------------------------------------------
# 4. Analyse each candidate group
# --------------------------------------------------

candidate_results = []
account_participation_records = []

candidate_ids = membership_data["candidate_id"].unique()


for candidate_id in candidate_ids:

    candidate_data = membership_data[
        membership_data["candidate_id"] == candidate_id
    ]

    cycle_count = len(candidate_data)

    # Store how many times each account appears
    account_counter = Counter()

    for _, row in candidate_data.iterrows():

        accounts_in_cycle = set(
            row[column]
            for column in account_columns
        )

        for account in accounts_in_cycle:
            account_counter[account] += 1

    account_count = len(account_counter)

    # Accounts appearing in more than one cycle
    repeated_accounts = {
        account: count
        for account, count in account_counter.items()
        if count > 1
    }

    accounts_in_multiple_cycles = len(repeated_accounts)

    # Find the maximum participation of one account
    if account_counter:
        highest_account_participation = max(
            account_counter.values()
        )
    else:
        highest_account_participation = 0

    # Avoid misleading concentration calculations
    if cycle_count == 1:

        structure_type = "Not applicable - single cycle"
        participation_share = None
        repeat_account_ratio = None

    else:

        participation_share = (
            highest_account_participation
            / cycle_count
        ) * 100

        repeat_account_ratio = (
            accounts_in_multiple_cycles
            / account_count
        ) * 100

        # Exploratory classification for multi-cycle groups
        if participation_share >= 50:

            structure_type = "Highly concentrated"

        elif participation_share >= 25:

            structure_type = "Moderately concentrated"

        else:

            structure_type = "Distributed"

    # Save candidate-level results
    candidate_results.append({

        "candidate_id": candidate_id,

        "account_count": account_count,

        "cycle_count": cycle_count,

        "highest_account_participation":
            highest_account_participation,

        "accounts_in_multiple_cycles":
            accounts_in_multiple_cycles,

        "highest_account_participation_share":
            participation_share,

        "repeat_account_ratio":
            repeat_account_ratio,

        "exploratory_structure_type":
            structure_type

    })

    # Save account-level participation
    for account, participation_count in account_counter.items():

        account_participation_records.append({

            "candidate_id": candidate_id,

            "account_id": account,

            "cycle_participation_count":
                participation_count

        })


# --------------------------------------------------
# 5. Convert results into DataFrames
# --------------------------------------------------

candidate_structure_data = pd.DataFrame(
    candidate_results
)

account_participation_data = pd.DataFrame(
    account_participation_records
)


# --------------------------------------------------
# 6. Identify hub accounts
# --------------------------------------------------

hub_accounts = account_participation_data[
    account_participation_data[
        "cycle_participation_count"
    ] > 1
].copy()

hub_accounts = hub_accounts.sort_values(
    by="cycle_participation_count",
    ascending=False
)


# --------------------------------------------------
# 7. Save output files
# --------------------------------------------------

candidate_structure_file = (
    OUTPUT_FOLDER / "candidate_structure_analysis.csv"
)

account_participation_file = (
    OUTPUT_FOLDER / "account_cycle_participation.csv"
)

hub_accounts_file = (
    OUTPUT_FOLDER / "candidate_hub_accounts.csv"
)


candidate_structure_data.to_csv(
    candidate_structure_file,
    index=False
)

account_participation_data.to_csv(
    account_participation_file,
    index=False
)

hub_accounts.to_csv(
    hub_accounts_file,
    index=False
)


# --------------------------------------------------
# 8. Print summary
# --------------------------------------------------

print("\nAnalysis completed successfully.")

print(
    "\nCandidate structure distribution:"
)

print(
    candidate_structure_data[
        "exploratory_structure_type"
    ].value_counts()
)


# Only analyse multi-cycle candidates
multi_cycle_candidates = candidate_structure_data[
    candidate_structure_data["cycle_count"] > 1
].copy()

multi_cycle_candidates = multi_cycle_candidates.sort_values(
    by="cycle_count",
    ascending=False
)


print(
    "\nTop multi-cycle candidate groups:"
)

print(
    multi_cycle_candidates[
        [
            "candidate_id",
            "account_count",
            "cycle_count",
            "highest_account_participation",
            "accounts_in_multiple_cycles",
            "highest_account_participation_share",
            "exploratory_structure_type"
        ]
    ].head(10).to_string(index=False)
)


print(
    "\nMost repeated accounts:"
)

print(
    hub_accounts.head(15).to_string(index=False)
)


print("\nFiles saved:")
print(candidate_structure_file)
print(account_participation_file)
print(hub_accounts_file)