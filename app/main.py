from fastapi import FastAPI, Request, WebSocket, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from app.db.base import Base, engine
from app.api.v1 import api_router as v1_router

# from starlette.middleware.sessions import SessionMiddleware
import logging
import os
import asyncio
# Threading
import threading
import time

from app.utils.consume_sqs_messages import consume_sqs_messages
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

# @app.on_event("startup")
# async def start_sqs_consumer():
#     # Start consuming messages on app startup
#     # asyncio.create_task(consume_sqs_messages())
#     threading.Thread(target=consume_sqs_messages, daemon=True).start()

# for v1
app.include_router(v1_router, prefix="/v1")
# app.include_router(v1_router, prefix="/v1")

# # Simulated data source for SSE
# async def event_generator():
#     count = 1
#     while True:
#         # Simulate real-time data
#         yield f"data: This is message {count}\n\n"
#         count += 1
#         await asyncio.sleep(2)  # Delay for 2 seconds

# @app.get("/stream")
# async def stream_events(request: Request):
#     """
#     SSE endpoint for streaming events to the client.
#     """
#     async def event_stream():
#         try:
#             async for event in event_generator():
#                 # If the client disconnects, stop streaming
#                 if await request.is_disconnected():
#                     print("Client disconnected")
#                     break
#                 yield event
#         except asyncio.CancelledError:
#             print("Stream cancelled")
    
#     return StreamingResponse(event_stream(), media_type="text/event-stream")



# @app.websocket("/ws")
# async def run_websocket(websocket: WebSocket):
#     # connect with new client
#     await websocket.accept()

#     try:
#         while True:
#             data = await websocket.receive_text()
#             message = f"Message from client: {data}"
#             await websocket.send_text(message)

#     except Exception as e:
#         print(e)



# Define a dependency
# def get_settings():
#     return {"app_name": "My FastAPI App", "version": "1.0.0"}

# def get_users():
#     return [
#         {"name": "Md Israil"},
#         {"name": "Md Salman"}
#     ]

# # Use the dependency in a route
# @app.get("/info")
# async def app_info(settings: dict = Depends(get_settings)):
#     return {"Application Name": settings["app_name"], "Version": settings["version"]}

# @app.get("/users/{user_id}")
# async def get_users(user_id: int, name: str, users: list = Depends(get_users)):
#     print(name)
#     filteredUsers = list(filter(lambda user: user["name"] == "Md Israil", users))
#     print(list(filteredUsers))
#     return filteredUsers



# @app.get("/results")
# async def get_results():
#     start = time.time()
#     response = {"message": "results called"}
#     elapsed = time.time() - start
#     print(f"Processing Time: {elapsed} seconds")
#     return response



# from concurrent.futures import ThreadPoolExecutor

# executor = ThreadPoolExecutor(max_workers=1)



# def thread_id():
#     return threading.current_thread().ident

# @app.get("/blocking")
# def blocking_task():
#     logging.info(f"Starting blocking task on thread {thread_id()}")
#     time.sleep(10)
#     logging.info(f"Finished blocking task on thread {thread_id()}")
#     return {"message": "Blocking task complete"}

# @app.get("/non-blocking")
# async def non_blocking_task():
#     logging.info(f"Starting non-blocking task on thread {thread_id()}")
#     await asyncio.sleep(30)
#     # time.sleep(30)
#     logging.info(f"Finished non-blocking task on thread {thread_id()}")
#     return {"message": "Non-blocking task complete"}






app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from the React app
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)















