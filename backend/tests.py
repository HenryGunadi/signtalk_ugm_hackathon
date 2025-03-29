import asyncio
import json
import websockets
from websockets import ServerConnection
import sys

async def keepAlive(websocket: ServerConnection) -> None:
    while True:
        try:
            pong_waiter = await websocket.ping()
            print(f"Pong : {pong_waiter}")
            print("Ping sent")
        except Exception as e:
            print(f"Ping failed : {e}")
            sys.exit()

        await asyncio.sleep(20) # <-- runs every n seconds

async def sendMessages(websocket: ServerConnection, testReqPayload):
    while True:
        try:
            message = await asyncio.to_thread(input, "Enter a message : ")
            testReqPayload["message"] = message
            await websocket.send(json.dumps(testReqPayload))
            print("Message sent!")
        except Exception as e:
            print(f"Something went wrong : {e}")
            break
        except websockets.ConnectionClosed as e:
            print(f"Connnection lost or server shuts down")
            break

        await asyncio.sleep(0.1)        

async def receiveMessages(websocket: ServerConnection):
    async for message in websocket:
        try:
            message = json.loads(message)
            print(f"CLIENT LOGS : {message}")
        except Exception as e:
            print(f"Something went wrong in receving message : {e}")
            break
        except websockets.ConnectionClosed as e:
            print(f"Connnection lost or server shuts down")
            break

        await asyncio.sleep(0.1)

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
            keep_alive = asyncio.create_task(keepAlive(websocket))

            await asyncio.gather(receive_task, send_task, keep_alive)
        except websockets.exceptions.ConnectionClosedError as e:
            print("Server shut down unexpectedly: ", e)
        except asyncio.CancelledError:
            print("Task was cancelled, possibly due to disconnection.")
        finally:
            print("Closing WebSocket connection...")
        
if __name__ == "__main__":
    asyncio.run(test())
