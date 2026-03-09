from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore
from uuid import uuid4
import os
from dotenv import load_dotenv

load_dotenv()

os.environ["NO_PROXY"] = "localhost,127.0.0.1"
os.environ["no_proxy"] = "localhost,127.0.0.1"  

model_name = "BAAI/bge-large-en-v1.5"
embeddings = FastEmbedEmbeddings(model_name=model_name, parallel=0)

QDRANT_URL = os.getenv("QDRANT_URL", "http://127.0.0.1:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")

def load_collection(documents):
    client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY
    )

    collection_name = "fitness_collection_instruction"

    existing_collections = [c.name for c in client.get_collections().collections]

    if collection_name not in existing_collections:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=client.get_embedding_size(model_name), 
                                        distance=Distance.COSINE)
        )
        
        vector_store = QdrantVectorStore(
            client=client,
            collection_name=collection_name,
            embedding=embeddings,
        )

        uuids = [str(uuid4()) for _ in range(len(documents))]
        
        vector_store.add_documents(documents=documents, ids=uuids)
    else:
        vector_store = QdrantVectorStore(
            client=client,
            collection_name=collection_name,
            embedding=embeddings,
        )
    
    return vector_store

def get_retriver(documents):
    vector_store = load_collection(documents)

    retriever = vector_store.as_retriever(search_type="mmr", search_kwargs={"k": 5})

    return retriever
    
    

    
    

