import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.stats import spearmanr, pearsonr




PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "richness_comparison.csv"
)


print("Loading richness comparison...")

data = pd.read_csv(INPUT_FILE)

data["Cai_Chao_ratio"] = (
    data["plant_diversity"] / data["Chao1"]
)


# =========================
# CORRELATIONS
# =========================

cai = data["plant_diversity"]
chao = data["Chao1"]


spearman_rho, spearman_p = spearmanr(
    cai,
    chao
)

pearson_r, pearson_p = pearsonr(
    cai,
    chao
)


print()
print("===================================")
print("Correlation analysis")
print("===================================")

print(f"Spearman rho: {spearman_rho:.3f}")
print(f"Spearman p-value: {spearman_p:.4f}")

print()

print(f"Pearson r: {pearson_r:.3f}")
print(f"Pearson p-value: {pearson_p:.4f}")

print()


ratio = data["Cai_Chao_ratio"]

completeness = data["Sampling_completeness_percent"]

ratio_rho, ratio_p = spearmanr(
    completeness,
    ratio
)

print()
print("===================================")
print("Sampling bias analysis")
print("===================================")

print(
    f"Spearman rho (completeness vs. Cai/Chao1): "
    f"{ratio_rho:.3f}"
)

print(
    f"p-value: {ratio_p:.4f}"
)
# =========================
# RANKINGS
# =========================

data["Cai_rank"] = (
    data["plant_diversity"]
    .rank(
        ascending=False,
        method="min"
    )
)

data["Chao1_rank"] = (
    data["Chao1"]
    .rank(
        ascending=False,
        method="min"
    )
)

data["Rank_difference"] = (
    data["Cai_rank"]
    - data["Chao1_rank"]
)


print("===================================")
print("Rank comparison")
print("===================================")

print(
    data[
        [
            "ECO_NAME",
            "Cai_rank",
            "Chao1_rank",
            "Rank_difference",
            "Cai_Chao_ratio"
        ]
    ]
    .sort_values("Cai_rank")
    .to_string(index=False)
)

print()


# =========================
# SAMPLING BIAS PLOT
# =========================

plt.figure(
    figsize=(9, 7),
    dpi=150
)

plt.scatter(
    completeness,
    ratio,
    s=80,
    edgecolors="black",
    linewidths=0.5
)


# Add ecoregion names

for _, row in data.iterrows():

    plt.annotate(
        row["ECO_NAME"],
        (
            row["Sampling_completeness_percent"],
            row["Cai_Chao_ratio"]
        ),
        xytext=(5, 5),
        textcoords="offset points",
        fontsize=7
    )


# Trend line

import numpy as np

slope, intercept = np.polyfit(
    completeness,
    ratio,
    1
)

x = np.linspace(
    completeness.min(),
    completeness.max(),
    100
)

y = slope * x + intercept

plt.plot(
    x,
    y,
    linestyle="--",
    linewidth=1
)


plt.xlabel(
    "Sampling completeness (%)"
)

plt.ylabel(
    "Cai predicted richness / GBIF Chao1"
)

plt.title(
    "Sampling Completeness vs. Richness Discrepancy"
)


plt.grid(
    alpha=0.2
)

plt.tight_layout()

plt.show()