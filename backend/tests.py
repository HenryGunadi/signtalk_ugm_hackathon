import asyncio
import json
import websockets
from websockets import ServerConnection

async def sendMessages(websocket: ServerConnection, testReqPayload):
    while True:
        message = input("New Message: ")
        testReqPayload["message"] = message
        await websocket.send(json.dumps(testReqPayload))
        print("Message sent!")
        await asyncio.sleep(0.2)

async def receiveMessages(websocket: ServerConnection):
    async for message in websocket:
        message = json.loads(message)
        print(f"CLIENT LOGS : {message}")

async def test():
    uri = "ws://localhost:8000"
    id = input("Create user ID: ")
    type = input("Type (create/join): ")

    testReqPayload = {"type": type, "id": id}

    if type == "join":
        testReqPayload["room_id"] = input("Room ID: ")

    testReqPayload["message"] = "Testing from client"

    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps(testReqPayload))
        data = await websocket.recv()
        message = json.loads(data)

        print("Message from server : ", message)
        try:
            receive_task = asyncio.create_task(receiveMessages(websocket))
            send_task = asyncio.create_task(sendMessages(websocket, testReqPayload))

            await asyncio.gather(receive_task, send_task)
        except websockets.exceptions.ConnectionClosedError as e:
            print("Server shut down unexpectedly: ", e)
        except asyncio.CancelledError:
            print("Task was cancelled, possibly due to disconnection.")
        
if __name__ == "__main__":
    asyncio.run(test())
