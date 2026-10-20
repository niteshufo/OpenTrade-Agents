
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.agents import router as agents_router
from app.database import Base, engine
from app.models.agent import Agent


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="OpenTrade Agents",
    description="An open-source crypto trading-agent platform",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(agents_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to OpenTrade Agents",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "opentrade-agents",
        "mode": "development",
    }
