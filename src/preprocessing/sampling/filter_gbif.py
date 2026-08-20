import geopandas as gpd
import pandas as pd
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


GBIF_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "gbif_occurrences.csv"
)

ECOREGIONS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "plant_diversity_ecoregions.gpkg"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "gbif_ecoregion_occurrences.csv"
)


print("Loading GBIF occurrences...")

gbif = pd.read_csv(GBIF_FILE)

print("GBIF records:", len(gbif))


# ==========================================
# CREATE GEOMETRY
# ==========================================

print("Creating points...")

gbif = gbif.dropna(
    subset=[
        "decimalLongitude",
        "decimalLatitude"
    ]
)

points = gpd.GeoDataFrame(
    gbif,
    geometry=gpd.points_from_xy(
        gbif["decimalLongitude"],
        gbif["decimalLatitude"]
    ),
    crs="EPSG:4326"
)


# ==========================================
# LOAD ECOREGIONS
# ==========================================

print("Loading ecoregions...")

ecoregions = gpd.read_file(
    ECOREGIONS_FILE
)
sampling = pd.read_csv(
    PROJECT_ROOT
    / "data"
    / "processed"
    / "sampling_bias.csv"
)

ecoregions = ecoregions[
    ecoregions["ECO_ID"].isin(sampling["ECO_ID"])
]

ecoregions = ecoregions[
    [
        "ECO_ID",
        "ECO_NAME",
        "plant_diversity",
        "geometry"
    ]
].drop_duplicates("ECO_ID")


ecoregions = ecoregions.to_crs(
    points.crs
)


# ==========================================
# SPATIAL JOIN
# ==========================================

print("Performing spatial join...")
points = points.drop(
    columns=["ECO_ID", "ECO_NAME"],
    errors="ignore"
)
joined = gpd.sjoin(
    points,
    ecoregions,
    how="inner",
    predicate="within"
)

joined = joined.rename(
    columns={
        "ECO_ID_right": "ECO_ID",
        "ECO_NAME_right": "ECO_NAME",
        "plant_diversity": "plant_diversity"
    }
)


# ==========================================
# SAVE
# ==========================================

print()
print("Records inside ecoregions:", len(joined))
print(
    "Unique ecoregions:",
    joined["ECO_ID"].nunique()
)


output = joined.drop(
    columns=["geometry", "index_right"]
)


output.to_csv(
    OUTPUT_FILE,
    index=False
)


print()
print("Saved:")
print(OUTPUT_FILE)