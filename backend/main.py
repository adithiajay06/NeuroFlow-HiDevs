from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting NeuroFlow API...")
    
    # Startup logic
    app.state.postgres = True
    app.state.redis = True
    app.state.mlflow = True

    yield

    # Shutdown logic
    print("Shutting down NeuroFlow API...")


# Create FastAPI app
app = FastAPI(
    title="NeuroFlow API",
    version="1.0.0",
    lifespan=lifespan
)

# OpenTelemetry middleware
FastAPIInstrumentor.instrument_app(app)


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "NeuroFlow API is running"
    }


# Health check endpoint
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "checks": {
            "postgres": app.state.postgres,
            "redis": app.state.redis,
            "mlflow": app.state.mlflow
        }
    }


# Metrics endpoint
@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    return """
# HELP neuroflow_requests_total Total requests
# TYPE neuroflow_requests_total counter
neuroflow_requests_total 1
"""
