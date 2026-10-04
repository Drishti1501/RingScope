import pandas as pd
from pathlib import Path

project_folder = Path(__file__).resolve().parent.parent

output_folder = project_folder / "outputs"

risk_data = pd.read_csv(
    output_folder / "account_network_metrics.csv"
)

# =====================================
# CREATE RISK INDICATORS
# =====================================

metrics = [
    "outgoing_amount",
    "unique_receivers",
    "incoming_amount",
    "unique_senders"
]

for metric in metrics:
    threshold = risk_data[metric].quantile(0.95)

    risk_data[metric + "_flag"] = (
        risk_data[metric] >= threshold
    ).astype(int)

# =====================================
# CALCULATE RISK SCORE
# =====================================

flag_columns = [
    "outgoing_amount_flag",
    "unique_receivers_flag",
    "incoming_amount_flag",
    "unique_senders_flag"
]

risk_data["risk_score"] = risk_data[flag_columns].sum(axis=1)

# =====================================
# RANK ACCOUNTS
# =====================================

risk_data = risk_data.sort_values(
    "risk_score",
    ascending=False
)

print("========== RISK SCORING ==========")

print("\nRisk score distribution:")
print(risk_data["risk_score"].value_counts().sort_index())

print("\nTop 20 accounts by risk score:")

print(
    risk_data[
        [
            "nodeid",
            "isFraud",
            "fraudStep",
            "risk_score",
            "outgoing_amount",
            "unique_receivers",
            "incoming_amount",
            "unique_senders"
        ]
    ].head(20)
)

# =====================================
# SAVE RESULTS
# =====================================

risk_data.to_csv(
    output_folder / "risk_scored_accounts.csv",
    index=False
)

print("\nRisk-scored dataset saved successfully.")