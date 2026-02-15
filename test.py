import requests
from dotenv import load_dotenv
load_dotenv()
# import os
# from fitness_application import db

def call_requests():
    URL="http://localhost:8000/question"

    DATA = {"question":"I just started going to the gym after a long time, what excercises can i do for my shoulder?"}
    try:
        response = requests.post(URL, json=DATA)
        print(f"Status Code: {response.status_code}")
        return response.json()
    except Exception as e:
        print(e)

    

def call_feed_back():
    URL="http://localhost:8000/feedback"
    
    DATA = {"feedback":1,
            "conversation_id":"265f2348-e349-4542-af1c-8d5f342f30a8"}
    try:
        response = requests.post(URL, json=DATA)
        print(f"Status Code: {response.status_code}")
        return response.json()
    except Exception as e:
        print(e)


# def get_convo():
#     res = db.get_recent_conversations()
#     return res


if __name__ == "__main__":
    response = call_feed_back()
    # response = get_convo()
    # response = call_requests()
    print(response)
