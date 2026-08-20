import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


# =========================
# FILES
# =========================

ECOREGIONS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "plant_diversity_ecoregions.gpkg"
)

CHAO_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "chao1.csv"
)

OUTPUT_TABLE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "richness_comparison.csv"
)


# =========================
# LOAD DATA
# =========================

print("Loading ecoregions...")

ecoregions = gpd.read_file(
    ECOREGIONS_FILE
)

print("Loading Chao1 results...")

chao = pd.read_csv(
    CHAO_FILE
)


# =========================
# SELECT CAI DATA
# =========================

cai = ecoregions[
    [
        "ECO_ID",
        "ECO_NAME",
        "plant_diversity"
    ]
].copy()


# One row per ecoregion
cai = cai.drop_duplicates(
    "ECO_ID"
)


# =========================
# MERGE DATA
# =========================

comparison = cai.merge(
    chao[
        [
            "ECO_ID",
            "GBIF_records",
            "Observed_species",
            "Chao1"
        ]
    ],
    on="ECO_ID",
    how="inner"
)


# =========================
# SAMPLING COMPLETENESS
# =========================

comparison["Sampling_completeness"] = (
    comparison["Observed_species"]
    / comparison["Chao1"]
)

comparison["Sampling_completeness_percent"] = (
    comparison["Sampling_completeness"]
    * 100
)


# =========================
# SORT
# =========================

comparison = comparison.sort_values(
    "plant_diversity",
    ascending=False
)


# =========================
# PRINT RESULTS
# =========================

print()
print("===================================")
print("Richness comparison")
print("===================================")

print(
    comparison[
        [
            "ECO_NAME",
            "plant_diversity",
            "GBIF_records",
            "Observed_species",
            "Chao1",
            "Sampling_completeness_percent"
        ]
    ].to_string(index=False)
)

print()


# =========================
# SAVE TABLE
# =========================

comparison.to_csv(
    OUTPUT_TABLE,
    index=False
)

print("Saved comparison table:")
print(OUTPUT_TABLE)


# =========================
# PLOT
# =========================

plt.figure(
    figsize=(10, 7),
    dpi=150
)


scatter = plt.scatter(
    comparison["plant_diversity"],
    comparison["Chao1"],
    c=comparison["Sampling_completeness_percent"],
    cmap="viridis",
    s=80,
    edgecolors="black",
    linewidths=0.5
)


# =========================
# 1:1 REFERENCE LINE
# =========================

min_value = min(
    comparison["plant_diversity"].min(),
    comparison["Chao1"].min()
)

max_value = max(
    comparison["plant_diversity"].max(),
    comparison["Chao1"].max()
)

plt.plot(
    [min_value, max_value],
    [min_value, max_value],
    linestyle="--",
    linewidth=1
)


# =========================
# LABELS
# =========================

for _, row in comparison.iterrows():

    plt.annotate(
        row["ECO_NAME"],
        (
            row["plant_diversity"],
            row["Chao1"]
        ),
        xytext=(5, 5),
        textcoords="offset points",
        fontsize=7
    )


# =========================
# COLORBAR
# =========================

plt.colorbar(
    scatter,
    label="Sampling completeness (%)"
)


# =========================
# AXES
# =========================

plt.xlabel(
    "Cai et al. predicted plant species richness"
)

plt.ylabel(
    "GBIF Chao1 estimated richness"
)

plt.title(
    "Predicted vs. Estimated Plant Species Richness",
    fontsize=15
)


plt.grid(
    alpha=0.2
)

plt.tight_layout()

plt.show()