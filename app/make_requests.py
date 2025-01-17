import asyncio
import httpx

API_URL = "http://localhost:8000/results"

async def send_request():
    async with httpx.AsyncClient() as client:
        response = await client.get(API_URL)
        print(response.status_code, response.json())

async def main():
    tasks = [send_request() for _ in range(100)]  # Create 100 tasks
    await asyncio.gather(*tasks)  # Run them concurrently

if __name__ == "__main__":
    asyncio.run(main())
