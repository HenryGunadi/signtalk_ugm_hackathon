import asyncio
import websockets

async def test():
    uri = "ws://localhost:8000"

    async with websockets.connect(uri) as websocket:
        await websocket.send("Hello Server!") # <-- send data back to client
        response = await websocket.recv()
        print(f"Server response : {response}")

if __name__ == "__main__":
    asyncio.run(test())