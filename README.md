# Fitness Assistant — RAG Application

![Fitness Assistant](image/fitness_desc.png)

Staying consistent with fitness routines is challenging, especially for beginners. Gyms can be intimidating, and personal trainers are not always available or affordable. The Fitness Assistant solves this by providing a conversational AI that gives personalised exercise recommendations, step-by-step instructions, and equipment-aware alternatives — on demand, through natural language.

Interact with the assistant directly on Telegram: [**@codeflamer_bot**](https://t.me/codeflamer_bot)

---

## Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Dataset](#dataset)
- [Technologies](#technologies)
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Running Locally](#running-locally)
- [Deployment](#deployment)
- [API Reference](#api-reference)
- [Evaluation](#evaluation)

---

## Project Overview

The Fitness Assistant is a Retrieval-Augmented Generation (RAG) application. When a user sends a fitness question via Telegram, the system retrieves the most relevant exercise records from a vector database and feeds them as context to a Mistral AI language model, which generates a grounded, accurate response.

The main use cases are:

1. **Exercise Selection** — Recommend exercises based on targeted muscle groups, activity type, or available equipment.
2. **Exercise Replacement** — Suggest suitable alternatives to a given exercise.
3. **Exercise Instructions** — Provide step-by-step guidance on how to perform a specific exercise correctly.
4. **Equipment Queries** — Describe what a piece of equipment looks like, including an image where available.

---

## Architecture

```
User (Telegram)
      │
      ▼
Telegram Bot  (Railway — Dockerfile.telegram)
      │
      │  HTTP (internal)
      ▼
FastAPI Application  (Railway)
      │
      ├──► Qdrant Cloud  ──► Exercise documents (vector embeddings)
      │         retrieval
      │
      ├──► Mistral AI    ──► Response generation + LLM-as-judge evaluation
      │
      └──► PostgreSQL    ──► Conversation & feedback storage
               │
               ▼
         Grafana Cloud   (private monitoring)
```

**Request flow:**

1. User sends a message to the Telegram bot.
2. The bot forwards the query to the FastAPI backend.
3. The query is embedded and used to retrieve the top-5 most relevant exercise documents from Qdrant (MMR search).
4. Retrieved documents and the user query are passed to Mistral AI, which generates a response.
5. The response is evaluated for relevance by a second LLM-as-judge call.
6. The conversation, token usage, cost, and relevance score are saved to PostgreSQL.
7. The bot sends the response back to the user with thumbs-up / thumbs-down feedback buttons.

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
| Vector Database  | [Qdrant Cloud](https://qdrant.tech/)                                           |
| Embeddings       | [FastEmbed](https://github.com/qdrant/fastembed) — `BAAI/bge-large-en-v1.5`    |
| API              | [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/) |
| Database         | [PostgreSQL](https://www.postgresql.org/) (Railway managed)                    |
| Monitoring       | [Grafana Cloud](https://grafana.com/) (private)                                |
| Telegram Client  | [python-telegram-bot](https://python-telegram-bot.org/)                        |
| Rate Limiting    | [SlowAPI](https://github.com/laurentS/slowapi)                                 |
| Hosting          | [Railway](https://railway.app/)                                                |
| Containerisation | [Docker](https://www.docker.com/)                                              |
| Package Manager  | [uv](https://github.com/astral-sh/uv)                                          |

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose (for local development)
- [uv](https://github.com/astral-sh/uv) (for running without Docker)
- A [Mistral AI API key](https://console.mistral.ai/)
- A [Telegram Bot token](https://core.telegram.org/bots#botfather)
- A [HuggingFace token](https://huggingface.co/settings/tokens)
- A [Qdrant Cloud](https://cloud.qdrant.io/) cluster and API key (free tier)

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
POSTGRES_HOST=your_postgres_host
POSTGRES_DB=your_database_name
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_strong_password
POSTGRES_PORT=5432

# Qdrant
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key

# Data
DATA_PATH=./data/data_clean.csv
```

> **Never commit your `.env` file.** It is already listed in `.gitignore`.

---

## Running Locally

### 1. Install uv

```bash
pip install uv
```

### 2. Create and activate a virtual environment

```bash
uv venv

# Windows
source .venv/Scripts/activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
uv pip install -r requirements.txt
```

### 4. Start PostgreSQL with Docker

```bash
docker-compose up postgres -d
```

Update your `.env` to use localhost:

```env
POSTGRES_HOST=localhost
```

### 5. Start the FastAPI application

```bash
uv run uvicorn api.main:app --reload
```

The database tables are created automatically on first startup.

### 6. Start the Telegram bot

```bash
uv run python clients/telegram_bot.py
```

Open Telegram, find your bot, and send a fitness question to test it.

### 7. Run tests

```bash
uv run python test.py
```

---

## Deployment

The application is hosted on [Railway](https://railway.app/) across two services backed by managed infrastructure.

### Infrastructure overview

| Service      | Platform          | Notes                                |
| ------------ | ----------------- | ------------------------------------ |
| FastAPI app  | Railway           | Built from `Dockerfile`              |
| Telegram bot | Railway           | Built from `Dockerfile.telegram`     |
| PostgreSQL   | Railway managed   | Connected via internal variables     |
| Qdrant       | Qdrant Cloud free | Connected via `QDRANT_URL`           |
| Monitoring   | Grafana Cloud     | Private, reads from Railway Postgres |

### Setting up on Railway

**1. Create a Railway project and connect your GitHub repo.**

**2. Add a managed PostgreSQL database:**

- In your project → **"+ New Service"** → **"Database"** → **"PostgreSQL"**
- Railway generates connection variables automatically.

**3. Configure the FastAPI app service variables:**

```
MISTRAL_API_KEY=your_mistral_api_key
HF_TOKEN=your_huggingface_token
DATA_PATH=./data/data_clean.csv
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key
POSTGRES_HOST=${{Postgres.PGHOST}}
POSTGRES_PORT=${{Postgres.PGPORT}}
POSTGRES_DB=${{Postgres.PGDATABASE}}
POSTGRES_USER=${{Postgres.PGUSER}}
POSTGRES_PASSWORD=${{Postgres.PGPASSWORD}}
```

**4. Add the Telegram bot as a second Railway service:**

- **"+ New Service"** → **"GitHub Repo"** → same repo
- In **Settings → Build → Dockerfile Path** set to: `Dockerfile.telegram`
- Set variables on the bot service:

```
TELEGRAM_TOKEN=your_telegram_bot_token
FASTAPI_URL=http://${{app.RAILWAY_PRIVATE_DOMAIN}}:8000
```

> The bot communicates with the FastAPI app over Railway's private internal network — the API is never exposed publicly.

**5. Set up Qdrant Cloud:**

- Create a free cluster at [cloud.qdrant.io](https://cloud.qdrant.io)
- Copy the cluster URL and API key into the Railway app service variables above.

### Creating a Telegram bot

If you need to create a new Telegram bot:

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` and follow the prompts
3. BotFather will give you a token — add it as `TELEGRAM_TOKEN` in your Railway bot service variables
4. Optionally send `/setdescription` and `/setuserpic` to customise the bot's profile

---

## API Reference

The API is not publicly exposed. All interaction goes through the Telegram bot. The endpoints below are for local development only.

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

---

## Evaluation

### Retrieval

Retrieval quality was measured using Hit Rate and Mean Reciprocal Rank (MRR) on a set of generated ground-truth question–document pairs.

| Approach                           | Hit Rate | MRR  |
| ---------------------------------- | -------- | ---- |
| Optimised (MMR, bge-large-en-v1.5) | 0.726    | 0.71 |

### RAG — LLM-as-Judge

Each generated response is automatically evaluated for relevance by a second Mistral AI call acting as a judge. Results across the evaluation set:

| Label        | Count | Percentage |
| ------------ | ----- | ---------- |
| RELEVANT     | 186   | 0.9        |
| NON_RELEVANT | 21    | 0.1        |
| **Total**    | 207   | 100%       |

### User Feedback

Feedback collected from real interactions via the thumbs-up / thumbs-down buttons:

| Signal                     | Count                 |
| -------------------------- | --------------------- |
| Thumbs up (relevant)       | <!-- To Be filled --> |
| Thumbs down (not relevant) | <!-- To be filled --> |
