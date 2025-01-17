from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
import asyncio
import httpx

app = FastAPI()
STOCK_API_URL = "https://api.example.com/stock"

# Shared set to track connected clients
connected_clients = set()

async def fetch_stock_data():
    """
    Fetch stock data and broadcast to all connected clients.
    Stop fetching if no clients are connected.
    """
    async with httpx.AsyncClient() as client:
        while connected_clients:  # Fetch only if clients are connected
            response = await client.get(STOCK_API_URL)
            data = response.json()  # Assuming the API returns JSON data
            
            # Broadcast data to all clients
            disconnected_clients = []
            for client in connected_clients:
                try:
                    await client.send_json(data)
                except:
                    # Track disconnected clients
                    disconnected_clients.append(client)
            
            # Remove disconnected clients
            for client in disconnected_clients:
                connected_clients.remove(client)

            await asyncio.sleep(1)  # Fetch every 1 second

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for clients to receive real-time stock updates.
    """
    await websocket.accept()
    connected_clients.add(websocket)
    
    try:
        # Start data fetching if this is the first client
        if len(connected_clients) == 1:
            asyncio.create_task(fetch_stock_data())
        
        # Keep the connection alive
        while True:
            await websocket.receive_text()  # Keep the connection active
    except Exception:
        pass
    finally:
        # Remove client when disconnected
        connected_clients.remove(websocket)
