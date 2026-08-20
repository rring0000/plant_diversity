import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PLANT_DIVERSITY_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "plant_diversity"
)

PROCESSED_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)

def load_plant_diversity():
    file = (
        PLANT_DIVERSITY_DIR 
         / "cai_etal_2022" 
         / "predictions"
         / "Predictions.csv"
    )

    data = pd.read_csv(file)

    data = data[
    (data["div"] == "sr") &
    (data["metric"] == "Prediction") &
    (data["model"] == "Ensemble")
    ]

    print(data.shape)

    print(
    data[
        (data["div"] == "sr") &
        (data["metric"] == "Prediction")
    ]["model"].value_counts()
    )

    print(data[data["grid_ID"] == 1][
    ["grid_ID", "gridsize", "interpolated", "value"]
])

    data = data[data["gridsize"] == 7774]
    data = data[["grid_ID", "value"]]

    data.to_csv(
    PROCESSED_DIR / "plant_diversity.csv",
    index=False,
)
    print(data.head())
    print(data.shape)
    print(data["grid_ID"].nunique())
    print(data["grid_ID"].duplicated().sum())
    

load_plant_diversity()

