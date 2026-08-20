import requests
import pandas as pd
from pathlib import Path
import geopandas as gpd
from shapely.geometry import Point

PROJECT_ROOT = Path(__file__).resolve().parents[3]

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
    / "sampling_bias.csv"
)


# ==========================================
# SETTINGS
# ==========================================

TOP_N = 10

# GBIF_LIMIT = 300
GBIF_LIMIT = 5000


# ==========================================
# LOAD ECOREGIONS
# ==========================================

print("Loading ecoregions...")

ecoregions = pd.DataFrame(
    __import__("geopandas").read_file(ECOREGIONS_FILE)
)

ecoregions = (
    ecoregions[
        ["ECO_ID", "ECO_NAME", "plant_diversity", "geometry"]
    ]
    .drop_duplicates("ECO_ID")
    .sort_values(
        "plant_diversity",
        ascending=False
    )
)

top_ecoregions = ecoregions.head(TOP_N)


print()
print("Selected ecoregions:")
print(
    top_ecoregions[
        ["ECO_ID", "ECO_NAME", "plant_diversity"]
    ]
)
print()


# ==========================================
# GBIF SEARCH
# ==========================================

def get_gbif_occurrences(ecoregion):

    name = ecoregion["ECO_NAME"]

    geometry = ecoregion["geometry"]

    minx, miny, maxx, maxy = geometry.bounds

    url = "https://api.gbif.org/v1/occurrence/search"

    limit = 300
    offset = 0
    max_records = 10000

    all_records = []

    while len(all_records) < max_records:

        params = {
            "scientificName": "Plantae",
            "decimalLongitude": f"{minx},{maxx}",
            "decimalLatitude": f"{miny},{maxy}",
            "limit": limit,
            "offset": offset,
            "hasCoordinate": "true",
        }

        response = requests.get(
            url,
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        records = data.get("results", [])

        if not records:
            break

        all_records.extend(records)

        print(
            f"  Downloaded: {len(all_records)}"
        )

        if len(records) < limit:
            break

        offset += limit

        if offset >= data.get("count", 0):
            break


    df = pd.DataFrame(all_records)

    return df

    return pd.DataFrame(all_records)


# ==========================================
# PROCESS GBIF DATA
# ==========================================

results = []
all_gbif_data = []


for _, ecoregion in top_ecoregions.iterrows():

    data = get_gbif_occurrences(ecoregion)
    data["ECO_ID"] = ecoregion["ECO_ID"]
    data["ECO_NAME"] = ecoregion["ECO_NAME"]

    all_gbif_data.append(data)

    if data.empty:

        print("  No records found.")
        continue

    if "species" not in data.columns:

        print("  No species information.")
        continue

    data = data.dropna(
        subset=["species"]
    )

    observed_species = (
        data["species"]
        .nunique()
    )

    records = len(data)

    singletons = (
        data["species"]
        .value_counts()
        .eq(1)
        .sum()
    )

    doubletons = (
        data["species"]
        .value_counts()
        .eq(2)
        .sum()
    )

    # --------------------------------------
    # Chao1
    # --------------------------------------

    if doubletons > 0:

        chao1 = (
            observed_species
            + (
                singletons ** 2
                / (2 * doubletons)
            )
        )

    else:

        chao1 = (
            observed_species
            + (
                singletons
                * (singletons - 1)
                / 2
            )
        )

    results.append({
        "ECO_ID": ecoregion["ECO_ID"],
        "ECO_NAME": ecoregion["ECO_NAME"],
        "Cai_prediction": ecoregion[
            "plant_diversity"
        ],
        "GBIF_records": records,
        "Observed_species": observed_species,
        "Singletons": singletons,
        "Doubletons": doubletons,
        "Chao1": chao1,
    })

    print(
        f"  Records: {records}"
    )

    print(
        f"  Observed species: "
        f"{observed_species}"
    )

    print(
        f"  Chao1: {chao1:.1f}"
    )

    print()


gbif_data = pd.concat(
    all_gbif_data,
    ignore_index=True
)

gbif_data.to_csv(
    PROJECT_ROOT
    / "data"
    / "processed"
    / "gbif_occurrences.csv",
    index=False,
)

print(
    f"Saved GBIF records: {len(gbif_data)}"
)


results = pd.DataFrame(results)

results.to_csv(
    OUTPUT_FILE,
    index=False,
)

print("===================================")
print("Sampling analysis complete.")
print("===================================")

print()

print(results)

print()

print(
    f"Saved to: {OUTPUT_FILE}"
)