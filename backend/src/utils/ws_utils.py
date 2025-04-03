from websockets import ServerConnection
import json

async def sendError(websocket: ServerConnection, message: str):
    event = {
        "type": "error",
        "message": message
    }

    await websocket.send(json.dumps(event))