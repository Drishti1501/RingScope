import pandas as pd
from pathlib import Path

# Find the project folder automatically
project_folder = Path(__file__).resolve().parent.parent

data_folder = (
    project_folder
    / "data"
    / "raw"
    / "aml_20k_combined"
)

files = ["nodes.csv", "transactions.csv"]

for file_name in files:
    file_path = data_folder / file_name

    print("\n" + "=" * 60)
    print(f"FILE: {file_name}")

    data = pd.read_csv(file_path)

    print("Rows and columns:", data.shape)
    print("\nColumn names:")
    print(list(data.columns))

    print("\nFirst 5 rows:")
    print(data.head())

    print("\nMissing values:")
    print(data.isnull().sum())