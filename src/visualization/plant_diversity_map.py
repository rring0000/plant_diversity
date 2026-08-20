import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import LogNorm
from pathlib import Path
from shapely.geometry import Point

PROJECT_ROOT = Path(__file__).resolve().parents[2]

FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "plant_diversity_ecoregions.gpkg"
)


print("Loading ecoregions...")

ecoregions = gpd.read_file(FILE)

print(ecoregions.head())
print()
print(ecoregions["plant_diversity"].describe())
print()

top3 = (
    ecoregions[
        ecoregions["plant_diversity"] > 0
    ]
    .sort_values("plant_diversity", ascending=False)
    .drop_duplicates("ECO_ID")
    .head(3)
)

# Only positive values for logarithmic scale
positive = ecoregions[
    ecoregions["plant_diversity"] > 0
]


fig, ax = plt.subplots(
    figsize=(11, 5.3),
    dpi=150
)


positive.plot(
    column="plant_diversity",
    cmap="turbo",
    norm=LogNorm(
        vmin=positive["plant_diversity"].min(),
        vmax=positive["plant_diversity"].max(),
    ),
    linewidth=0,
    legend=True,
    ax=ax,
)

top3_text = "TOP 3 ECOREGIONS\n\n"

for i, (_, row) in enumerate(top3.iterrows(), start=1):
    top3_text += (
        f"{i}. {row['ECO_NAME']}\n"
        f"   {row['plant_diversity']:.0f}\n"
    )

ax.text(
    0.02,
    0.05,
    top3_text,
    transform=ax.transAxes,
    fontsize=7,
    verticalalignment="bottom",
    bbox=dict(
        boxstyle="round,pad=0.4",
        facecolor="white",
        alpha=0.9,
        edgecolor="gray",
    ),
)

ax.set_title(
    "Predicted Plant Species Richness by Ecoregion",
    fontsize=18,
)


ax.set_axis_off()

# =========================
# HOVER INFORMATION
# =========================

def on_move(event):

    if event.inaxes != ax or event.xdata is None or event.ydata is None:
        return

    point = Point(event.xdata, event.ydata)

    matches = ecoregions[
        ecoregions.geometry.contains(point)
    ]

    if not matches.empty:

        region = matches.iloc[0]

        fig.canvas.toolbar.set_message(
            f"{region['ECO_NAME']} | "
            f"Plant diversity: {region['plant_diversity']:.0f}"
        )

    else:

        fig.canvas.toolbar.set_message(
            f"x={event.xdata:.2f}, y={event.ydata:.2f}"
        )


fig.canvas.mpl_connect(
    "motion_notify_event",
    on_move
)


plt.tight_layout()

plt.show()