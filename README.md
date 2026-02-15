# RAG-FITNESS-ASSISTANT

Staying consistent with fitness routines is challenging,
especially for beginners. Gyms can be intimidating, and personal
trainers aren't always available.

The Fitness Assistant provides a conversational AI that helps
users choose exercises and find alternatives, making fitness more
manageable.

## Project overview

The Fitness Assistant is a RAG application designed to assist
users with their fitness routines.

The main use cases include:

1. Exercise Selection: Recommending exercises based on the type
   of activity, targeted muscle groups, or available equipment.
2. Exercise Replacement: Replacing an exercise with suitable
   alternatives.
3. Exercise Instructions: Providing guidance on how to perform a
   specific exercise.
4. Conversational Interaction: Making it easy to get information
   without sifting through manuals or websites.

## Dataset

The dataset used in this project contains information about
various exercises, including:

- **Exercise Name:** The name of the exercise (e.g., Push-Ups, Squats).
- **Type of Activity:** The general category of the exercise (e.g., Strength, Mobility, Cardio).
- **Type of Equipment:** The equipment needed for the exercise (e.g., Bodyweight, Dumbbells, Kettlebell).
- **Body Part:** The part of the body primarily targeted by the exercise (e.g., Upper Body, Core, Lower Body).
- **Type:** The movement type (e.g., Push, Pull, Hold, Stretch).
- **Muscle Groups Activated:** The specific muscles engaged during
  the exercise (e.g., Pectorals, Triceps, Quadriceps).
- **Instructions:** Step-by-step guidance on how to perform the
  exercise correctly.

The dataset was generated using ChatGPT and contains 207 records. It serves as the foundation for the Fitness Assistant's exercise recommendations and instructional support.

## Technologies

- Minsearch - for searching

- MISTRAl AI as an LLM

* FLASK as the API interface

## Preparing the application

## Running without Docker

If you dont want to use docker, you can run manually and have to install all the necessary dependencies

You can run it in a virtual environment
This project made use of `uv`

```bash
    uv python install
```

you can create and spin up a virrtual environment using the follow command, of you are on windows

```bash
    uv venv
    source .venv/Scripts/activate
```

```bash
    uv pip install -r requirements.txt
```

Running the command below will automatically initialize the database, and starts running the app

```bash
  uv run python fitness_application/app.py
```

### Using Requests

When the application is running, you can use [requests](https://requests.readthedocs.io/en/latest/) to send questions—use test.py for testing it:

```bash
  uv run python test.py
```

## Running it with Docker

Using docker makes it easy to run the application

```bash
docker-compose up
```

If you need to change something in the dockerfile and test quickly, you can use the following commands:

```bash
docker build -t fitness-buddy .

docker run -t  \
 -e MISTRAL_KEY=${MISTRAL_KEY} \
 -e DATA_PATH="data/data_unclean.csv" \
 -p 8000:8000 \
 fitness-buddy


# docker run -t -e MISTRAL_KEY=%MISTRAL_KEY% -e DATA_PATH=data/data_unclean.csv -p 8000:8000 fitness-buddy
```

### Using Requests

When the application is running, you can use [requests](https://requests.readthedocs.io/en/latest/) to send questions—use test.py for testing it:

```bash
  uv run python test.py
```

## MISC

```bash
URL="http://127.0.0.1:8000"

DATA='{"question":"I want some core excercises that also helps my back"}'

curl -X POST ${URL}/question \
-H "Content-Type: application/json" \
-d "${DATA}"
```

This is an example of the response,

```json
{
  "answer": "Based on the **CONTEXT**, the best **core exercise that also helps your back** is:\n\n### **Superman Exercise**\n- **Muscle Groups Activated:** Lower Back, Glutes, Hamstrings\n- **Instructions:** Lie face down on the floor with arms extended. Lift your arms, chest, and legs off the ground simultaneously, then lower them back down.\n\nThis exercise strengthens your **lower back** while engaging your **core** for stability.",
  "conversation_id": "1f440215-b880-4d4e-88ac-6f21804d1583",
  "question": "I want some core excercises that also helps my back"
}
```

Sending feedback

```bash
ID="1f440215-b880-4d4e-88ac-6f21804d1583"

URL="http://127.0.0.1:8000"

FEEDBACK_DATA="{
    \"conversation_id\":\"${ID}\",
    \"feedback\": 1
}"

curl -X POST ${URL}/feedback \
-H "Content-Type: application/json" \
-d "${FEEDBACK_DATA}"
```

An example of response from this request is:

```json
{
  "message": "Feedback received for conversation 1f440215-b880-4d4e-88ac-6f21804d1583: 1"
}
```

## Interface

We use Flask for serving the application as API

Refert to ["Running the Application's section"](#running-it)

## Ingestion

The ingestion script is written in [fitness_application/ingest.py](fitness_application/ingest.py), and it is run on app start up

## Evaluation

To check the code for retrival, you can check out the [Fitness_Assistant.ipynb](Fitness_Assistant.ipynb) notebook

### Retrival

The basic approach without using boosting functionality in minsearch givs the following result:
{'hit_rate': 0.851207729468599, 'mrr': 0.7854543363239016}

The improved version with an optimized boosting paramater gave:
{'hit_rate': 0.8473429951690822, 'mrr': 0.8062905452035889}

The best boosting parameters

```bash
    boost = {
        'exercise_name': 2.11,
        'type_of_activity': 1.46,
        'type_of_equipment': 0.65,
        'body_part': 2.65,
        'type': 1.31,
        'muscle_groups_activated': 2.54,
        'instructions': 0.74
    }
```

## Ragflow

I used the LLM-as-a-judge evaluation metrics for the RAg flow generation;
Among 1035 records, We had:

- X: RELAVANT - 0.835
- Y: PARTLY_REVELANT - 0.150
- Z: IRRELEVANT - 0.015

(Can tryo ot different models and different prompts to compare which is better than the current prompt and model I have)

### monitoring

Grafana was used for the monitoring the app;ication

Its accessible at (http://localhost:3000/)

### Containerization

### Reproducibility

-m make docker for the application also run tin docker compose automatically

- include the environment variables

- a cli code to run code too or a frontend
