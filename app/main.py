from fastapi import FastAPI
from app.db.base import Base, engine
from app.api.v1 import api_router as v1_router

Base.metadata.create_all(bind=engine)

app = FastAPI()
# for v1
app.include_router(v1_router, prefix="/v1", tags=["videos"])




























