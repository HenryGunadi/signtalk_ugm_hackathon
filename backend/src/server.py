# web socket for exhanging ice and sdp in signaling between users
import json
import asyncio
import uuid
from websockets.asyncio.server import serve, broadcast
from typing import List
from websockets import ServerConnection

# === UTILS ===
async def sendError(websocket: ServerConnection, message: str):
    event = {
        "type": "error",
        "message": message
    }

    await websocket.send(json.dumps(event))

def broadcastMessage(room: 'Room', message, *args) -> None:
    print("Message in broadcast : ", message)
    print("Message type : ", type(message))

    try:
        # broadcast to other people excluding the user itself
        if args is not None:
            excluded_users: List[User] = list(filter(lambda user: user.websocket != args[0], room.connected_participants))
            excluded_websockets = [user.websocket for user in excluded_users]

            broadcast(excluded_websockets, json.dumps(message))
        else:
            # broadcast to all users in the room
            broadcast([user.websocket for user in room.connected_participants], message)
    except TypeError as e:
        print(f"Message is incorrect type")
        raise
    except Exception as e:
        print(f"Broadcast error unexpectedly : {e}") 
        raise
    
# === Classes ===
class Room():
    def __init__(self, id):
        self.connected_participants: List[User] = []
        self.room_id = id
        
    async def addUser(self, new_user: 'User') -> None:
        for user in self.connected_participants:
            if new_user.id == user.id:
                await new_user.websocket.send("User already exists in the room.")

                return

        self.connected_participants.append(new_user)

    def removeUser(self, websocket: ServerConnection) -> None:
        self.connected_participants = [
            user for user in self.connected_participants if user.websocket != websocket 
        ]

        print("User removed.")

class User():
    def __init__(self, id, websocket: ServerConnection, room: Room):
        self.id = id
        self.websocket: ServerConnection = websocket
        self.room = room

    async def sendChatMessage(self, message) -> None:
        try:
            if not isinstance(message, str):
                raise TypeError("Message is not a string!")
            
            # else broadcast to the room including him/her self
            await broadcastMessage(self.room, message)
        except TypeError as e:
            print(str(e))
            await sendError(self.websocket, str(e))
            return
        except Exception as e:
            print(f"Unexpected error in sendChatMessage: {e}")
            await sendError(self.websocket, f"Unexpected error in sendChatMessage: {e}")
            return

    async def leaveRoom(self) -> None:
        await self.room.removeUser(self.websocket)

    # user in the call
    async def inCall(self) -> None:
        try:
            print(f"User id : {self.id} connected to the call")
            async for message in self.websocket:
                print("trigerred")
                data = json.loads(message)
                print(f"SERVER LOGS : {data}")

                # first handle if its a sdp or ice offer
                if data['type'] in ["offer", "answer"]:
                    for user in self.room.connected_participants:
                        if user.websocket != self.websocket:
                            await user.websocket.send(json.dumps(data["sdp"]))
                
                """
                    Handle audio and video stream. Process it as input to the ai model
                    and give back the output to clients
                """

                # # DEMO WITH SIMPLE TEXTS
                broadcastMessage(self.room, data["message"], self.websocket)
                # another_user = next((user for user in self.room.connected_participants if user.websocket != self.websocket))

                # TESTING
                # await self.websocket.send(json.dumps(data['message']))
                print("sent!")
        except Exception as e:
            print(f"Unexpected error in inCall: {e}")
        finally:
            try:
            # user disconnects
                self.room.removeUser(self.websocket)
                await broadcastMessage(self.room, f"User : {self.id} disconnected.", self.websocket)
                del self
            except Exception as e:
                print(f"Broadcast error : {e}")
                del self

class App():
    def __init__(self):
        self.rooms: List[Room] = []

    def addRooms(self, room: Room) -> None:
        self.rooms.append(room)

    def deleteRoom(self, room_id: str) -> None:
        self.rooms = [
            room for room in self.rooms if room.room_id != room_id
        ]

class Server():
    def __init__(self, app: App):
        self.app: App = app
    
    # start the websocket server
    async def run(self) -> None:
        # websocket is passed here
        async with serve(self.handler, "localhost", 8000) as server:
            try:
                print("Websocket server is running on port 8000")
                await server.serve_forever()
            except asyncio.CancelledError:
                print("Server shutting down...")

    async def handler(self, websocket: ServerConnection) -> None:
        try:
            message = await websocket.recv()
            print("Message from client : ", message)
            event: dict = json.loads(message)

            await websocket.send(json.dumps({"response": "Hello from server"}))
            # dummyIdKey = str(uuid.uuid4())
            dummyKey = "hello"

            # create a call room
            if event.get("type") == "create":
                room = Room(dummyKey) # <-- FIX LATER OR MANUALLY INSERT ROOM_ID!!
                user = User(event.get("id"), websocket, room)
                await room.addUser(user)
                self.app.addRooms(room)

                # user is in the call
                await user.inCall()
            elif event.get("type") == "join": # <-- join a room
                room_id = event.get("room_id")
                
                for room in self.app.rooms:
                    if room.room_id == room_id:
                        user = User(event.get("id"), websocket, room)
                        await room.addUser(user)

                        # user joined the call
                        await user.inCall()

                # invalid room_id key
                await sendError(websocket, "Invalid room key")
            else:
                logs = "Event type not found!" 
                print(logs)
                await websocket.send(logs)
        except Exception as e:
            print(f"Handler error: {e}")
            await sendError(websocket, str(e))

if __name__ == "__main__":
    app = App()
    server = Server(app)

    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(server.run())