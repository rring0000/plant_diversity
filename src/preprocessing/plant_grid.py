import geopandas as gpd
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

HEXAGON_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "plant_diversity"
    / "cai_etal_2022"
    / "data"
    / "Hexagons"
    / "grid_8_lm_isl_clipped.shp"
)

def load_plant_grid():
    grid = gpd.read_file(HEXAGON_FILE)

    print(grid.crs)

    data = pd.read_csv(
    PROJECT_ROOT
    / "data"
    / "processed"
    / "plant_diversity.csv"
)
    merged = grid.merge(
        data,
        left_on="g_8__ID",
        right_on="grid_ID",
        how="inner",
    )
    merged = merged[["g_8__ID", "value", "geometry"]]

    

    print(merged.head())
    print(merged.shape)
    print(merged.crs)

    merged.to_file(
    PROJECT_ROOT
    / "data"
    / "processed"
    / "plant_diversity_grid.gpkg",
    layer="plant_diversity",
    driver="GPKG",
)

load_plant_grid()
