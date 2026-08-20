import pandas as pd
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "gbif_ecoregion_occurrences.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "chao1.csv"
)


print("Loading GBIF ecoregion occurrences...")

data = pd.read_csv(INPUT_FILE)

print("Records:", len(data))
print("Ecoregions:", data["ECO_ID"].nunique())
print()


results = []


for eco_id, group in data.groupby("ECO_ID"):

    eco_name = group["ECO_NAME"].iloc[0]

    # Remove records without species identification
    species = group["species"].dropna()

    # Number of records for each species
    frequencies = species.value_counts()

    # Observed species richness
    observed_species = len(frequencies)

    # Singletons
    F1 = (frequencies == 1).sum()

    # Doubletons
    F2 = (frequencies == 2).sum()

    # Chao1 estimator
    if F2 > 0:
        chao1 = observed_species + (
            F1 ** 2 / (2 * F2)
        )
    else:
        chao1 = float("nan")

    results.append({
        "ECO_ID": eco_id,
        "ECO_NAME": eco_name,
        "GBIF_records": len(group),
        "Observed_species": observed_species,
        "Singletons": F1,
        "Doubletons": F2,
        "Chao1": chao1
    })


results = pd.DataFrame(results)


# Sort by Chao1
results = results.sort_values(
    "Chao1",
    ascending=False
)


print("===================================")
print("Chao1 analysis complete.")
print("===================================")

print(results.to_string(index=False))

print()


results.to_csv(
    OUTPUT_FILE,
    index=False
)

print("Saved to:")
print(OUTPUT_FILE)