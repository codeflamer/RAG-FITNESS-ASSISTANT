from minsearch import Index
import pandas as pd
import os

DATA_PATH = os.getenv("DATA_PATH", "./data/data_unclean.csv")

def ingest_data(data_path=DATA_PATH):
    df = pd.read_csv(data_path)

    documents = df.to_dict(orient="records")


    index = Index(
        text_fields=[
            'exercise_name',
            'type_of_activity', 
            'body_part',
            "type_of_equipment",
            'type', 
            'muscle_groups_activated', 
            'instructions'
        ],
        keyword_fields=[""]
    )
    index.fit(documents)


    return index