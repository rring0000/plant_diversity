import pandas as pd
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "chao1.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "sampling_completeness.csv"
)


print("Loading Chao1 results...")

data = pd.read_csv(INPUT_FILE)


# Sampling completeness
data["Sampling_completeness"] = (
    data["Observed_species"] / data["Chao1"]
)


# Percentage
data["Sampling_completeness_percent"] = (
    data["Sampling_completeness"] * 100
)


data = data.sort_values(
    "Sampling_completeness",
    ascending=False
)


print()
print("===================================")
print("Sampling completeness")
print("===================================")

print(
    data[
        [
            "ECO_NAME",
            "GBIF_records",
            "Observed_species",
            "Chao1",
            "Sampling_completeness_percent"
        ]
    ].to_string(index=False)
)

print()


data.to_csv(
    OUTPUT_FILE,
    index=False
)


print("Saved to:")
print(OUTPUT_FILE)