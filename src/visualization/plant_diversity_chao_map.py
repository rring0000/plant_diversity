import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import LogNorm
from pathlib import Path
from shapely.geometry import Point


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

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

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "plant_diversity_chao_comparison.png"
)


# ============================================================
# LOAD DATA
# ============================================================

print("Loading ecoregions...")

ecoregions = gpd.read_file(
    ECOREGIONS_FILE
)

print("Loading Chao1 results...")

chao = pd.read_csv(
    CHAO_FILE
)


# ============================================================
# CLEAN ECO_ID
# ============================================================

ecoregions["ECO_ID"] = pd.to_numeric(
    ecoregions["ECO_ID"],
    errors="coerce"
)

chao["ECO_ID"] = pd.to_numeric(
    chao["ECO_ID"],
    errors="coerce"
)


# ============================================================
# ORIGINAL CAI VALUE
# ============================================================

ecoregions["Cai_plant_diversity"] = (
    ecoregions["plant_diversity"]
)


# ============================================================
# JOIN CHAO1
# ============================================================

print("Joining Chao1 data...")

ecoregions = ecoregions.merge(
    chao[
        [
            "ECO_ID",
            "Chao1",
            "Observed_species",
            "GBIF_records"
        ]
    ],
    on="ECO_ID",
    how="left"
)


# ============================================================
# CHAO1-CORRECTED VALUE
# ============================================================

ecoregions["Chao_corrected"] = (
    ecoregions["Cai_plant_diversity"]
)

mask = ecoregions["Chao1"].notna()

ecoregions.loc[
    mask,
    "Chao_corrected"
] = ecoregions.loc[
    mask,
    "Chao1"
]


# ============================================================
# PRINT COMPARISON
# ============================================================

print()
print("===================================")
print("Cai → Chao1 replacements")
print("===================================")

comparison = ecoregions.loc[
    mask,
    [
        "ECO_ID",
        "ECO_NAME",
        "Cai_plant_diversity",
        "Chao1",
        "Observed_species",
        "GBIF_records"
    ]
].copy()

comparison["Change_percent"] = (
    (
        comparison["Chao1"]
        - comparison["Cai_plant_diversity"]
    )
    / comparison["Cai_plant_diversity"]
    * 100
)

print(
    comparison.to_string(index=False)
)


# ============================================================
# POSITIVE VALUES
# ============================================================

positive = ecoregions[
    ecoregions["Cai_plant_diversity"] > 0
].copy()


# ============================================================
# COMMON COLOR SCALE
# ============================================================

all_values = pd.concat(
    [
        ecoregions.loc[
            ecoregions["Cai_plant_diversity"] > 0,
            "Cai_plant_diversity"
        ],
        ecoregions.loc[
            ecoregions["Chao_corrected"] > 0,
            "Chao_corrected"
        ]
    ]
)

norm = LogNorm(
    vmin=all_values.min(),
    vmax=all_values.max()
)


# ============================================================
# TOP 3
# ============================================================

top3_original = (
    ecoregions[
        ecoregions["Cai_plant_diversity"] > 0
    ]
    .sort_values(
        "Cai_plant_diversity",
        ascending=False
    )
    .drop_duplicates("ECO_ID")
    .head(3)
)

top3_corrected = (
    ecoregions[
        ecoregions["Chao_corrected"] > 0
    ]
    .sort_values(
        "Chao_corrected",
        ascending=False
    )
    .drop_duplicates("ECO_ID")
    .head(3)
)


# ============================================================
# FIGURE
# ============================================================

fig, axes = plt.subplots(
    1,
    2,
    figsize=(18, 7),
    dpi=120
)


# ============================================================
# LEFT — CAI
# ============================================================

left_data = positive.copy()

left_data.plot(
    column="Cai_plant_diversity",
    cmap="turbo",
    norm=norm,
    linewidth=0,
    legend=False,
    ax=axes[0]
)

axes[0].set_title(
    "Original Cai et al. prediction",
    fontsize=16
)

axes[0].set_axis_off()


# ============================================================
# RIGHT — CHAO1
# ============================================================

right_data = positive.copy()

right_data.plot(
    column="Chao_corrected",
    cmap="turbo",
    norm=norm,
    linewidth=0,
    legend=False,
    ax=axes[1]
)

axes[1].set_title(
    "GBIF Chao1-corrected richness",
    fontsize=16
)

axes[1].set_axis_off()


# ============================================================
# TOP 3 BOXES
# ============================================================

top3_text = "TOP 3 ECOREGIONS\n\n"

for i, (_, row) in enumerate(
    top3_original.iterrows(),
    start=1
):
    top3_text += (
        f"{i}. {row['ECO_NAME']}\n"
        f"   {row['Cai_plant_diversity']:.0f}\n"
    )

axes[0].text(
    0.02,
    0.04,
    top3_text,
    transform=axes[0].transAxes,
    fontsize=7,
    verticalalignment="bottom",
    bbox=dict(
        boxstyle="round,pad=0.4",
        facecolor="white",
        alpha=0.9,
        edgecolor="gray"
    )
)


top3_text = "TOP 3 ECOREGIONS\n\n"

for i, (_, row) in enumerate(
    top3_corrected.iterrows(),
    start=1
):
    top3_text += (
        f"{i}. {row['ECO_NAME']}\n"
        f"   {row['Chao_corrected']:.0f}\n"
    )

axes[1].text(
    0.02,
    0.04,
    top3_text,
    transform=axes[1].transAxes,
    fontsize=7,
    verticalalignment="bottom",
    bbox=dict(
        boxstyle="round,pad=0.4",
        facecolor="white",
        alpha=0.9,
        edgecolor="gray"
    )
)


# ============================================================
# SHARED COLORBAR
# ============================================================

sm = plt.cm.ScalarMappable(
    norm=norm,
    cmap="turbo"
)

sm.set_array([])

cbar = fig.colorbar(
    sm,
    ax=axes,
    fraction=0.025,
    pad=0.02
)

cbar.set_label(
    "Estimated plant species richness",
    fontsize=12
)


# ============================================================
# HOVER INFORMATION
# ============================================================

def on_move(event):

    # Mouse isn't over either map
    if event.inaxes not in axes:
        return

    if event.xdata is None or event.ydata is None:
        return

    point = Point(
        event.xdata,
        event.ydata
    )

    matches = ecoregions[
        ecoregions.geometry.contains(point)
    ]

    if matches.empty:

        fig.canvas.toolbar.set_message("")

        return

    region = matches.iloc[0]

    # --------------------------------------------------------
    # LEFT MAP
    # --------------------------------------------------------

    if event.inaxes == axes[0]:

        fig.canvas.toolbar.set_message(
            f"{region['ECO_NAME']} | "
            f"Cai plant diversity: "
            f"{region['Cai_plant_diversity']:.0f}"
        )

    # --------------------------------------------------------
    # RIGHT MAP
    # --------------------------------------------------------

    elif event.inaxes == axes[1]:

        if pd.notna(region["Chao1"]):

            fig.canvas.toolbar.set_message(
                f"{region['ECO_NAME']} | "
                f"Chao1: "
                f"{region['Chao1']:.0f} | "
                f"Cai: "
                f"{region['Cai_plant_diversity']:.0f}"
            )

        else:

            fig.canvas.toolbar.set_message(
                f"{region['ECO_NAME']} | "
                f"Cai plant diversity: "
                f"{region['Cai_plant_diversity']:.0f}"
            )


fig.canvas.mpl_connect(
    "motion_notify_event",
    on_move
)


# ============================================================
# TITLE
# ============================================================

fig.suptitle(
    "Plant Species Richness: Cai et al. vs. GBIF Chao1",
    fontsize=20,
    y=0.98
)


# ============================================================
# SAVE
# ============================================================

plt.tight_layout(
    rect=[0, 0, 1, 0.95]
)

plt.savefig(
    OUTPUT_FILE,
    dpi=250,
    bbox_inches="tight"
)

print()
print("Saved:")
print(OUTPUT_FILE)


# ============================================================
# SHOW
# ============================================================

plt.show()