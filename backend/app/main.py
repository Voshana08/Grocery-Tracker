from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import create_db_and_tables
from app.routes import locations


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="Grocery Tracker", lifespan=lifespan)
app.include_router(locations.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}
