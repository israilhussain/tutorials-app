from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.base import Base, engine
from app.api.v1 import api_router as v1_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Allow your React app (running at localhost:3000)
origins = [
    "http://localhost:3000",  # React app running locally
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows requests from the React app
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# for v1
app.include_router(v1_router, prefix="/v1", tags=["videos"])




























