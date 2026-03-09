# Fitness Assistant — RAG Application

Staying consistent with fitness routines is challenging, especially for beginners. Gyms can be intimidating, and personal trainers are not always available or affordable. The Fitness Assistant solves this by providing a conversational AI that gives personalised exercise recommendations, step-by-step instructions, and equipment-aware alternatives — on demand, through natural language.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Dataset](#dataset)
- [Technologies](#technologies)
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Running with Docker (Recommended)](#running-with-docker-recommended)
- [Running without Docker](#running-without-docker)
- [API Reference](#api-reference)
- [Frontend Interfaces](#frontend-interfaces)
- [Monitoring](#monitoring)
- [Evaluation](#evaluation)

---

## Project Overview

The Fitness Assistant is a Retrieval-Augmented Generation (RAG) application. When a user asks a fitness question, the system retrieves relevant exercise records from a vector database (Qdrant) and feeds them as context to a Mistral AI language model, which generates a grounded, accurate response.

The main use cases are:

1. **Exercise Selection** — Recommend exercises based on targeted muscle groups, activity type, or available equipment.
2. **Exercise Replacement** — Suggest suitable alternatives to a given exercise.
3. **Exercise Instructions** — Provide step-by-step guidance on how to perform a specific exercise correctly.
4. **Equipment Queries** — Describe what a piece of equipment looks like, including an image where available.

---

## Architecture

```
User (Telegram / Streamlit / curl)
        │
        ▼
  FastAPI Application  (port 8000)
        │
        ├──► Qdrant Vector Store  ──► Exercise documents (embeddings)
        │         retrieval
        │
        ├──► Mistral AI (LLM)     ──► Response generation + LLM-as-judge evaluation
        │
        └──► PostgreSQL           ──► Conversation & feedback storage
                │
                ▼
           Grafana Dashboard  (port 3000)
```

**Request flow:**

1. User sends a query via Telegram, Streamlit, or directly via the API.
2. The query is embedded and used to retrieve the top-5 most relevant exercise documents from Qdrant (MMR search).
3. Retrieved documents + the user query are passed to Mistral AI, which generates a response.
4. The response is evaluated for relevance by a second LLM-as-judge call.
5. The conversation, token usage, cost, and relevance score are saved to PostgreSQL.
6. Grafana reads from PostgreSQL to display live monitoring metrics.

---

## Dataset

The dataset contains 207 exercise records generated with ChatGPT. Each record includes:

| Field                     | Description                                                     |
| ------------------------- | --------------------------------------------------------------- |
| `exercise_name`           | Name of the exercise (e.g., Push-Ups, Squats)                   |
| `type_of_activity`        | General category (e.g., Strength, Mobility, Cardio)             |
| `type_of_equipment`       | Equipment required (e.g., Bodyweight, Dumbbells, Kettlebell)    |
| `body_part`               | Primary body area targeted (e.g., Upper Body, Core, Lower Body) |
| `type`                    | Movement type (e.g., Push, Pull, Hold, Stretch)                 |
| `muscle_groups_activated` | Specific muscles engaged (e.g., Pectorals, Triceps, Quadriceps) |
| `instructions`            | Step-by-step instructions for correct form                      |
| `image_url`               | URL of an equipment/exercise image where available              |

The dataset is stored at `data/data_clean.csv` and is loaded into Qdrant on first startup.

---

## Technologies

| Component        | Technology                                                                     |
| ---------------- | ------------------------------------------------------------------------------ |
| LLM              | [Mistral AI](https://mistral.ai) (`mistral-large-latest`)                      |
| RAG Framework    | [LangChain](https://www.langchain.com/)                                        |
| Vector Database  | [Qdrant](https://qdrant.tech/)                                                 |
| Embeddings       | [FastEmbed](https://github.com/qdrant/fastembed) — `BAAI/bge-large-en-v1.5`    |
| API              | [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/) |
| Database         | [PostgreSQL 13](https://www.postgresql.org/)                                   |
| Monitoring       | [Grafana](https://grafana.com/)                                                |
| Telegram Client  | [python-telegram-bot](https://python-telegram-bot.org/)                        |
| Streamlit Client | [Streamlit](https://streamlit.io/)                                             |
| Rate Limiting    | [SlowAPI](https://github.com/laurentS/slowapi)                                 |
| Containerisation | [Docker](https://www.docker.com/) + Docker Compose                             |
| Package Manager  | [uv](https://github.com/astral-sh/uv)                                          |

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- [uv](https://github.com/astral-sh/uv) (for running without Docker)
- A [Mistral AI API key](https://console.mistral.ai/)
- A [Telegram Bot token](https://core.telegram.org/bots#botfather) (only if using the Telegram interface)
- A [HuggingFace token](https://huggingface.co/settings/tokens) (for downloading embeddings model)

---

## Environment Setup

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
# API Keys
MISTRAL_API_KEY=your_mistral_api_key
TELEGRAM_TOKEN=your_telegram_bot_token
HF_TOKEN=your_huggingface_token

# FastAPI
FASTAPI_URL=http://127.0.0.1:8000
APP_PORT=8000

# PostgreSQL
POSTGRES_HOST=postgres
POSTGRES_DB=fitness_database
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_strong_password
POSTGRES_PORT=5432

# Qdrant
QDRANT_URL=http://qdrant:6333

# Data
DATA_PATH=./data/data_clean.csv

# Grafana
GRAFANA_URL=http://localhost:3000
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=your_strong_grafana_password
GRAFANA_SECRET_KEY=your_random_secret_key
```

> **Never commit your `.env` file.** It is already listed in `.gitignore`.

---

## Running with Docker (Recommended)

Docker Compose starts all services — PostgreSQL, Qdrant, the FastAPI app, and Grafana — in the correct order with a single command.

### Start all services

```bash
docker-compose up
```

To run in the background:

```bash
docker-compose up -d
```

### Service URLs

| Service            | URL                        |
| ------------------ | -------------------------- |
| FastAPI            | http://localhost:8000      |
| API Docs (Swagger) | http://localhost:8000/docs |
| Grafana            | http://localhost:3000      |

### Initialise Grafana

After all services are running, set up the Grafana datasource and dashboard:

```bash
cd grafana
uv run python init.py
```

This creates a PostgreSQL datasource and imports the pre-built monitoring dashboard automatically.

### Start the Telegram bot

The Telegram bot runs as a separate process outside Docker:

```bash
uv run python clients/telegram_bot.py
```

### Start the Streamlit interface

```bash
uv run streamlit run clients/streamlit.py
```

### Rebuild after code changes

```bash
docker-compose up --build
```

### Stop all services

```bash
docker-compose down
```

To also remove stored data volumes:

```bash
docker-compose down -v
```

---

## Running without Docker

### 1. Install Python and uv

```bash
# Install uv if not already installed
pip install uv
```

### 2. Create a virtual environment

```bash
uv venv
```

Activate it:

```bash
# Windows
source .venv/Scripts/activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
uv pip install -r requirements.txt
```

### 4. Start PostgreSQL and Qdrant

You still need running instances of PostgreSQL and Qdrant. The easiest way is to start just those two services with Docker:

```bash
docker-compose up postgres qdrant -d
```

Update your `.env` to point to `localhost` instead of the Docker service names:

```env
POSTGRES_HOST=localhost
QDRANT_URL=http://localhost:6333
```

### 5. Start the FastAPI application

```bash
uv run uvicorn api.main:app --reload
```

The database tables are created automatically on first startup.

### 6. Start the Telegram bot (optional)

```bash
uv run python clients/telegram_bot.py
```

### 7. Start the Streamlit interface (optional)

```bash
uv run streamlit run clients/streamlit.py
```

### 8. Test the application

```bash
uv run python test.py
```

---

## API Reference

### Health check

```bash
GET http://localhost:8000/api/v1/health
```

```json
{ "status": "ok", "version": "1.0.0" }
```

### Send a chat query

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "I want core exercises that also help my back", "source": "cmd", "user": "demo"}'
```

Example response:

```json
{
  "answer": {
    "message": "Based on your goal, here are some core exercises that also strengthen your back:\n\n### Superman Exercise\n- **Muscles:** Lower Back, Glutes, Hamstrings\n- **Instructions:** Lie face down, extend arms forward. Lift arms, chest, and legs simultaneously, hold briefly, then lower.",
    "image_urls": [],
    "conversation_id": "1f440215-b880-4d4e-88ac-6f21804d1583"
  },
  "source": "cmd"
}
```

### Submit feedback

```bash
curl -X POST http://localhost:8000/api/v1/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "1f440215-b880-4d4e-88ac-6f21804d1583",
    "feedback": "relevant",
    "source": "cmd"
  }'
```

Accepted `feedback` values: `"relevant"` or `"not_relevant"`.

### Rate limiting

All endpoints are rate-limited to **2 requests per minute** per IP address.

### Interactive API docs

Full Swagger UI is available at:

```
http://localhost:8000/docs
```

---

## Frontend Interfaces

### Telegram Bot

After starting the bot with `uv run python clients/telegram_bot.py`, open your bot in Telegram and send any fitness-related message. The bot will:

1. Forward your message to the FastAPI backend.
2. Reply with the generated answer and any exercise images.
3. Present thumbs-up / thumbs-down feedback buttons.

### Streamlit

After starting Streamlit, open http://localhost:8501 in your browser. The interface provides a chat window, displays exercise images inline, and allows you to submit relevance feedback.

---

## Monitoring

Grafana is available at http://localhost:3000 after running `grafana/init.py`.

The dashboard includes:

- Total conversations over time
- Average response time
- Token usage and estimated Mistral API cost per query
- Relevance score distribution (RELEVANT / PARTLY_RELEVANT / NON_RELEVANT)
- Thumbs-up vs thumbs-down feedback ratio

Log into Grafana with the credentials set in your `.env` (`GRAFANA_ADMIN_USER` / `GRAFANA_ADMIN_PASSWORD`).

To inspect the database directly:

```bash
docker exec -it llm-fitness-postgres-1 psql -U your_username -d fitness_database
```

---

## Evaluation

### Retrieval

Retrieval quality was measured using Hit Rate and Mean Reciprocal Rank (MRR) on a set of generated ground-truth question–document pairs.

| Approach                           | Hit Rate         | MRR              |
| ---------------------------------- | ---------------- | ---------------- |
| Baseline (no boosting)             | <!-- fill in --> | <!-- fill in --> |
| Optimised (MMR, bge-large-en-v1.5) | <!-- fill in --> | <!-- fill in --> |

### RAG — LLM-as-Judge

Each generated response is automatically evaluated for relevance by a second Mistral AI call acting as a judge. Results across the evaluation set:

| Label           | Count            | Percentage       |
| --------------- | ---------------- | ---------------- |
| RELEVANT        | <!-- fill in --> | <!-- fill in --> |
| PARTLY_RELEVANT | <!-- fill in --> | <!-- fill in --> |
| NON_RELEVANT    | <!-- fill in --> | <!-- fill in --> |
| **Total**       | <!-- fill in --> | 100%             |

### User Feedback

Feedback collected from real interactions via the thumbs-up / thumbs-down buttons:

| Signal                     | Count            |
| -------------------------- | ---------------- |
| Thumbs up (relevant)       | <!-- fill in --> |
| Thumbs down (not relevant) | <!-- fill in --> |
