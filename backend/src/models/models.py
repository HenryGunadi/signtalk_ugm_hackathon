from websockets import ServerConnection, broadcast
from typing import List
from utils import ws_utils
import json

class Room():
    def __init__(self, id):
        self.connected_participants: List[User] = []
        self.room_id = id
        
    async def addUser(self, new_user: 'User') -> None:
        for user in self.connected_participants:
            if new_user.email == user.email:
                await new_user.websocket.send("User already exists in the room.")

                return

        self.connected_participants.append(new_user)

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
    def __init__(self, email:str, name:str, password: str, websocket: ServerConnection = None, room: Room = None):
        self.email = email
        self.name = name
        self.password = password
        self.websocket: ServerConnection = websocket
        self.room = room

    async def sendChatMessage(self, message) -> None:
        try:
            if not isinstance(message, str):
                raise TypeError("Message is not a string!")
            
            # else broadcast to the room including him/her self
            await self.room.broadcastMessage(self.room, message)
        except TypeError as e:
            print(str(e))
            await ws_utils.sendError(self.websocket, str(e))
            return
        except Exception as e:
            print(f"Unexpected error in sendChatMessage: {e}")
            await ws_utils.sendError(self.websocket, f"Unexpected error in sendChatMessage: {e}")
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
                self.room.broadcastMessage(self.room, data["message"], self.websocket)
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
                await self.room.broadcastMessage(self.room, f"User : {self.id} disconnected.", self.websocket)
                del self
            except Exception as e:
                print(f"Broadcast error : {e}")
                del self
                
    def to_dict(self) -> dict:
        return {
            "email": self.email,
            "name": self.name,
            "password": self.password
        }