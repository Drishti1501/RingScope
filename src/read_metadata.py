from pathlib import Path

project_folder = Path(__file__).resolve().parent.parent

metadata_path = (
    project_folder
    / "data"
    / "raw"
    / "aml_20k_combined"
    / "metadata.txt"
)

print("========== AMLSim METADATA ==========")

with open(metadata_path, "r", encoding="utf-8") as file:
    metadata = file.read()

print(metadata)