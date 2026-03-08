from fastapi import FastAPI
# from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.responses import JSONResponse
# from prometheus_fastapi_instrumentator import Instrumentator
from api.middleware.throttle import limiter
from api.routes import chat, health, feedback

from dotenv import load_dotenv
load_dotenv()

from fitness_application import db
print("Initializing database...")
db.init_db()
print("✓ Database initialized")

app = FastAPI(title="Fitness Assistant API", version="1.0.0")

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"error": "Too many requests. Please wait a minute before trying again."}
    )

# Routes
app.include_router(chat.router, prefix="/api/v1",tags=["chat"])

app.include_router(health.router, prefix="/api/v1", tags=["health"])

app.include_router(feedback.router, prefix="/api/v1", tags=["feedback"])