# web socket for exhanging ice and sdp in signaling between users
import json
import asyncio
import uuid
from websockets.asyncio.server import serve, broadcast
from typing import List
from websockets import ServerConnection
from aiortc import MediaStreamTrack, MediaStreamError, RTCPeerConnection, RTCSessionDescription


# === UTILS ===
async def sendError(websocket: ServerConnection, message: str):
    event = {
        "type": "error",
        "message": message
    }

    await websocket.send(json.dumps(event))

def log_info(msg, *args, **kwargs):
        print({kwargs.get("user_id")} + "" + msg, *args)

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
        
        # send broadcast that another user has join to notify users to make sdp exchange
        excluded_users: List[User] = list(filter(lambda user: user.websocket != new_user.websocket, self.connected_participants))
        exlcuded_websockets = [user.websocket for user in excluded_users]
        message = {
            "user_id": new_user.id,
            "type": "join"
        }        
        
        broadcast(exlcuded_websockets, json.dumps(message))       
    def removeUser(self, websocket: ServerConnection) -> None:
        self.connected_participants = [
            user for user in self.connected_participants if user.websocket != websocket 
        ]

        print("User removed.")
        
    def broadcastMessage(self, message, *args) -> None:
        print("Message in broadcast : ", message)
        print("Message type : ", type(message))

        try:
            # broadcast to other people excluding the user itself
            if args is not None:
                excluded_users: List[User] = list(filter(lambda user: user.websocket != args[0], self.connected_participants))
                
                excluded_websockets = [user.websocket for user in excluded_users]

                broadcast(excluded_websockets, json.dumps(message))
            else:
                # broadcast to all users in the room
                broadcast([user.websocket for user in self.connected_participants], message)
        except TypeError as e:
            print(f"Message is incorrect type")
            raise
        except Exception as e:
            print(f"Broadcast error unexpectedly : {e}") 
            raise

class User():
    def __init__(self, id, websocket: ServerConnection, room: Room, pc: RTCPeerConnection = None):
        self.id = id
        self.websocket: ServerConnection = websocket
        self.pc: RTCPeerConnection = pc
        self.room: Room = room

    async def sendChatMessage(self, message) -> None:
        try:
            if not isinstance(message, str):
                raise TypeError("Message is not a string!")
            
            # else broadcast to the room including him/her self
            await self.room.broadcastMessage(message)
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
                data = json.loads(message)
                print(f"SERVER LOGS : {data}")

                """
                    WAITING FOR BT TO CONTINUEEE
                """

                # first handle if its a sdp or ice offer
                if data['type'] in ["offer", "answer"]:
                    payload = {
                        "type": data["type"],
                        "sdp": data["sdp"],
                        "user_id": self.id
                    }

                    for user in self.room.connected_participants: # <-- FIX IT LATER
                        if user.websocket != self.websocket:
                            await user.websocket.send(json.dumps(payload))

                """
                    Handle audio and video stream. Process it as input to the ai model
                    and give back the output to clients
                """

                ## DEMO WITH SIMPLE TEXTS
                self.room.broadcastMessage(data["message"], self.websocket)
        except Exception as e:
            print(f"Unexpected error in inCall: {e}")
        finally:
            try:
            # user disconnects
                self.room.removeUser(self.websocket)
                await self.room.broadcastMessage(f"User : {self.id} disconnected.", self.websocket)
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
                room = Room(dummyKey) # <-- FIX it LATER OR MANUALLY INSERT ROOM_ID!!
                user = User(event.get("id"), websocket, room)
                await room.addUser(user)
                self.app.addRooms(room) # <-- FIX it later, integrate with real time db

                # user is in the call
                await user.inCall()
            elif event.get("type") == "join": # <-- join a room
                room_id = event.get("room_id")
                
                for room in self.app.rooms: # <-- FIX IT LATER
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