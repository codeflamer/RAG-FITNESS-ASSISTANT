from fastapi import FastAPI
# from slowapi import _rate_limit_exceeded_handler
# from slowapi.errors import RateLimitExceeded
# from slowapi.middleware import SlowAPIMiddleware
# from starlette.responses import JSONResponse
# from prometheus_fastapi_instrumentator import Instrumentator
# from api.middleware.throttle import limiter
from api.routes import chat, health, feedback

from dotenv import load_dotenv
load_dotenv()

from fitness_application import db
print("Initializing database...")
db.init_db()
print("✓ Database initialized")

app = FastAPI(title="Fitness Assistant API", version="1.0.0")

# Routes
app.include_router(chat.router, prefix="/api/v1",tags=["chat"])

app.include_router(health.router, prefix="/api/v1", tags=["health"])

app.include_router(feedback.router, prefix="/api/v1", tags=["feedback"])