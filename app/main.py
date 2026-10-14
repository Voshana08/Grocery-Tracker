from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import create_db_and_tables
from app.routes import locations


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="Grocery Tracker", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(locations.router)


@app.get("/")
def home():
    return {"message": "Grocery Tracker is running"}


@app.get("/health")
def health():
    return {"status": "ok"}
