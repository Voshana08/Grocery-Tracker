from fastapi import FastAPI

app = FastAPI(title="Grocery Tracker")


@app.get("/")
def home():
    return {"message": "Grocery Tracker is running"}


@app.get("/health")
def health():
    return {"status": "ok"}
