import os

from dotenv import load_dotenv

load_dotenv()  # reads .env into environment variables

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./grocery.db")
