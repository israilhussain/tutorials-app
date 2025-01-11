from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.base import Base, engine
from app.api.v1 import api_router as v1_router

# from starlette.middleware.sessions import SessionMiddleware
import logging
import os

# from fastapi_auth.auth import get_current_user, authenticate_user, create_access_token
# from fastapi_auth.database import get_db
# from sqlalchemy.orm import Session

Base.metadata.create_all(bind=engine)


# Define your log directory (local Windows path)
log_directory = "C:\\app\\logs"

# Ensure the directory exists
os.makedirs(log_directory, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Log everything at the DEBUG level and higher
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
    handlers=[
        logging.FileHandler(os.path.join(log_directory, "server.log")),  # Save logs to a file
        logging.StreamHandler()  # Also log to console
    ]
)

logger = logging.getLogger(__name__)


app = FastAPI()

# Add SessionMiddleware to manage sessions (cookies)
# app.add_middleware(SessionMiddleware, secret_key="test123")

# Allow your React app (running at localhost:3000)
origins = [
    "http://localhost:3000",  # React app running locally
    "https://dev-ik6pjv551ifjn6il.us.auth0.com"  # Auth0 domain,
    "http://localhost:8000",

]



# for v1
app.include_router(v1_router, prefix="/v1")
# app.include_router(v1_router, prefix="/v1")




app.add_middleware(
    CORSMiddleware,
    allow_origins=[origins],  # Allows requests from the React app
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)






















