from pathlib import Path
import pandas as pd


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
OUTPUT_FOLDER = PROJECT_FOLDER / "outputs"


files_to_check = [
    "final_candidate_features.csv",
    "candidate_investigation_analysis.csv",
    "candidate_structure_analysis.csv",
    "cycle_investigation_table.csv"
]


for filename in files_to_check:

    file_path = OUTPUT_FOLDER / filename

    print("\n" + "=" * 70)
    print(filename)
    print("=" * 70)

    data = pd.read_csv(file_path)

    print("Rows:", len(data))
    print("Columns:")
    print(list(data.columns))

    print("\nFirst 3 rows:")
    print(data.head(3).to_string(index=False))