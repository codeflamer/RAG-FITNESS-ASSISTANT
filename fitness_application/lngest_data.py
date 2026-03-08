import os
from langchain_community.document_loaders.csv_loader import CSVLoader

DATA_PATH = os.getenv("DATA_PATH", "./data/data_clean.csv")

def lngest_data(data_path=DATA_PATH):
    # data_dir="data/data_clean.csv"
    loader = CSVLoader(
        file_path=DATA_PATH,
        content_columns=["instructions", "exercise_name",'type_of_activity', 'type_of_equipment','body_part','type','muscle_groups_activated'],        
        metadata_columns=['id', 'exercise_name', 'type_of_activity', 'type_of_equipment','body_part','type','muscle_groups_activated','instructions', "image_url"]  
    )


    documents = loader.load()

    return documents
