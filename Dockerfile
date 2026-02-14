FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install uv

RUN uv pip install --system --no-cache-dir -r requirements.txt

COPY data/data_unclean.csv data/data_unclean.csv

COPY fitness_application .

EXPOSE 8000

CMD gunicorn --bind 0.0.0.0:8000 app:app