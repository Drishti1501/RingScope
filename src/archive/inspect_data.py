import pandas as pd
from pathlib import Path

data_folder = Path("../data/raw")

files = [
    "accounts.csv",
    "alerts.csv",
    "cash_tx.csv",
    "tx.csv"
]

for file_name in files:
    file_path = data_folder / file_name

    print("\n" + "=" * 50)
    print(f"FILE: {file_name}")

    data = pd.read_csv(file_path)

    print("Rows and columns:", data.shape)
    print("Column names:", list(data.columns))
    print("\nFirst 5 rows:")
    print(data.head())
    print("\nMissing values:")
    print(data.isnull().sum())