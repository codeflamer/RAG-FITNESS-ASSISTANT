import requests
from dotenv import load_dotenv
load_dotenv()
import os
from fitness_application import db

def call_requests():
    print(os.getenv("POSTGRES_USER"))
    URL="http://localhost:8000/question"

    DATA = {"question":"I need calf excercises"}

    response = requests.post(URL, json=DATA)

    return response.json()

def call_feed_back():
    res = db.save_feedback("291914c3-5a7b-430a-9040-e5d2c167401d", 1)

    return res


def get_convo():
    res = db.get_recent_conversations()
    return res


if __name__ == "__main__":
    # response = call_feed_back()
    response = get_convo()
    # response = call_requests()
    print(response)
