# web socket for exhanging ice and sdp in signaling between users
import json
import asyncio
import uuid
from websockets.asyncio.server import serve, broadcast
from typing import List

# === UTILS ===
async def sendError(websocket, message: str):
    event = {
        "type": "error",
        "message": message
    }

    await websocket.send(json.dumps(event))

async def broadcastMessage(room, message) -> None:
    try:
        broadcast(room, message)
    except Exception as e:
        print(f"Unexpected error : {e}")
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

        self.connected_participants.append(new_user)

    async def removeUser(self, websocket) -> None:
        self.connected_participants = [
            user for user in self.connected_participants if user.websocket != websocket 
        ]    

class User():
    def __init__(self, id, websocket, room: Room):
        self.id = id
        self.websocket = websocket
        self.room = room

    async def sendChatMessage(self, message) -> None:
        try:
            if not isinstance(message, str):
                raise TypeError("Message is not a string!")
            
            # else broadcast to the room
            broadcastMessage(self.room, message)
        except TypeError as e:
            print(str(e))
            await sendError(self.websocket, str(e))
            return
        except Exception as e:
            print(f"Unexpected error in sendChatMessage: {e}")
            await sendError(self.websocket, f"Unexpected error in sendChatMessage: {e}")
            return

    async def leaveRoom(self) -> None:
        self.room.removeUser(self.websocket)

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

    async def run(self) -> None:
        async with serve(self.handler, "localhost", 8000) as server:
            print("Websocket server is running on port 8000")
            await server.serve_forever()

    async def handler(self, websocket) -> None:
        message = await websocket.recv()
        event: dict = json.loads(message)
        
        # create a call room
        if event.get("type") == "create":
            room = Room(str(uuid.uuid4())) # <-- FIX LATER OR MANUALLY INSERT ROOM_ID!!
            user = User(event.get("id"), websocket, room)
            room.addUser(user)
            self.app.addRooms(room)

            # user is in a call
            
        elif event.get("type") == "join":
            room_id = event.get("room_id")
            
            # join room
            for room in self.app.rooms:
                if room.room_id == room_id:
                    user = User(event.get("id"), websocket, room)
                    room.addUser(user)
        else:
            logs = "Event type not found!" 
            print(logs)
            await websocket.send(logs) # <-- send back response to client

if __name__ == "__main__":
    app = App()
    server = Server(app)

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(server.run())