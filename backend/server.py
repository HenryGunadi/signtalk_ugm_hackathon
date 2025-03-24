import asyncio
import websockets
from typing import List

class User():
    def __init__(self, ip: str):
        self.ip = ip

    @property   
    def ip(self):
        return self.__ip

    @ip.setter
    def ip(self, ip):
        try:
            if ip == "" or ip is None:
                raise ValueError("Ip cannot be empty")
        except ValueError as e:
            print(f"ValueError: {e}")

        self.__ip = ip

class WebSocketConnection():
    def __init__(self):
        self.__users: List[User] = [] # initialize empty users

    # add user to the connection
    def addUser(self, user: User):
        if not isinstance(user, User):
            raise TypeError("User must be a user type!")
        
        self.users.append(user)

    @property
    def users(self) -> List[User]:
        return self.__users
    
    @users.setter
    def users(self, users: List[User]) -> None:
        if not isinstance(users, list) or not all(isinstance(u, User) for u in users):
            raise TypeError("Users must be a list of User instances")

        self.__users = users

async def echo(websocket):
    print("Client connected")
    try:
        async for message in websocket:
            print(f"Message from Client : {message}")
            await websocket.send("Hi from server!")
    except websockets.ConnectionClosed:
        print("Client disconnected!")

async def main():
    async with websockets.serve(echo, "localhost", 8000):
        print("Websocket is running")
        await asyncio.Future() # <-- Keeps the server running forever

if __name__ == "__main__":
    asyncio.run(main())