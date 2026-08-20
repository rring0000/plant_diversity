import geopandas as gpd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ECOREGIONS_FILE = (
    PROJECT_ROOT
    / "data"
    / "WWF"
    / "wwf_terr_ecos.shp"
)


def load_ecoregions():

    print("Loading ecoregions...")

    ecoregions = gpd.read_file(ECOREGIONS_FILE)

    print("Loading plant diversity grid...")

    plant_grid = gpd.read_file(
        PROJECT_ROOT
        / "data"
        / "processed"
        / "plant_diversity_grid.gpkg"
    )

    # Equal-area projection for area calculations
    ecoregions = ecoregions.to_crs("EPSG:6933")
    plant_grid = plant_grid.to_crs("EPSG:6933")

    print("Creating spatial overlay...")

    overlay = gpd.overlay(
        plant_grid,
        ecoregions,
        how="intersection",
    )

    print("Overlay shape:", overlay.shape)

    # Area of each grid/ecoregion intersection
    overlay["overlap_area"] = overlay.geometry.area

    # Value weighted by overlap area
    overlay["weighted_value"] = (
        overlay["value"] * overlay["overlap_area"]
    )

    # Aggregate by ecoregion
    result = (
        overlay
        .groupby(["ECO_ID", "ECO_NAME"])
        .agg(
            weighted_sum=("weighted_value", "sum"),
            total_overlap_area=("overlap_area", "sum"),
        )
        .reset_index()
    )

    # Area-weighted mean plant diversity
    result["plant_diversity"] = (
        result["weighted_sum"]
        / result["total_overlap_area"]
    )

    # Remove invalid ecoregion IDs
    result = result[result["ECO_ID"] > 0]

    print()
    print(result.head())
    print()
    print(result["plant_diversity"].describe())
    print()

    top3 = (
    result
    .sort_values("plant_diversity", ascending=False)
    .head(3)
)

    print()
    print("TOP 3 ECOREGIONS")
    print(top3[["ECO_NAME", "plant_diversity"]])
    print()

    # Save table
    result[
        ["ECO_ID", "ECO_NAME", "plant_diversity"]
    ].to_csv(
        PROJECT_ROOT
        / "data"
        / "processed"
        / "ecoregion_plant_diversity.csv",
        index=False,
    )

    # Convert back to geographic coordinates for mapping
    ecoregions_map = ecoregions.to_crs("EPSG:4326")

    map_data = ecoregions_map.merge(
        result[
            ["ECO_ID", "ECO_NAME", "plant_diversity"]
        ],
        on=["ECO_ID", "ECO_NAME"],
        how="inner",
    )

    print("Mapped ecoregions:", map_data.shape)

    print("Rows:", len(map_data))
    print("Unique ECO_ID:", map_data["ECO_ID"].nunique())
    print("Duplicated ECO_ID:", map_data["ECO_ID"].duplicated().sum())

    map_data = map_data.dissolve(
        by=["ECO_ID", "ECO_NAME"],
        aggfunc={
            "plant_diversity": "first"
        },
        as_index=False,
    )

    print("After dissolve:", map_data.shape)
    print("Unique ECO_ID:", map_data["ECO_ID"].nunique())

        # Save final map layer
    map_data.to_file(
        PROJECT_ROOT
        / "data"
        / "processed"
        / "plant_diversity_ecoregions.gpkg",
        layer="plant_diversity",
        driver="GPKG",
    )

    print("Saved ecoregion plant diversity.")


if __name__ == "__main__":
    load_ecoregions()