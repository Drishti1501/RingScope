import pandas as pd
from pathlib import Path

project_folder = Path(__file__).resolve().parent.parent

risk_data = pd.read_csv(
    project_folder
    / "outputs"
    / "risk_scored_accounts.csv"
)

# Fraud rate by risk score
evaluation = risk_data.groupby("risk_score").agg(
    total_accounts=("nodeid", "count"),
    fraud_accounts=("isFraud", "sum")
).reset_index()

evaluation["fraud_rate"] = (
    evaluation["fraud_accounts"]
    / evaluation["total_accounts"]
    * 100
)

print("========== RISK SCORE EVALUATION ==========")

print(evaluation)

# Overall fraud rate
overall_fraud_rate = risk_data["isFraud"].mean() * 100

print("\nOverall fraud-label rate:",
      round(overall_fraud_rate, 2), "%")

# Score 4 analysis
score_4 = risk_data[risk_data["risk_score"] == 4]

print("\nScore 4 accounts:", len(score_4))
print("Fraud-labeled score 4 accounts:",
      score_4["isFraud"].sum())

print(
    "Score 4 fraud rate:",
    round(score_4["isFraud"].mean() * 100, 2),
    "%"
)