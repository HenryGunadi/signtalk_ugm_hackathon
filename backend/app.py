from flask import Flask, request, jsonify
from aiortc import RTCPeerConnection, MediaStreamTrack
from flask_sockets import Sockets
from flask_cors import CORS

app = Flask(__name__)
sockets = Sockets(app)

CORS(
    app,
    resources={r"/*": {"origins": "*"}}, 
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE"],
)

@sockets.route("/ws")
def echo_socket(ws):
    while not ws.closed:
        message = ws.receive()
        ws.send(message)

@app.route("/offer", methods=["POST"])
def handle_offer():
    offer = request.json['sdp']
    pc = RTCPeerConnection()
    pc.setRemoteDescription(offer)

    # create an answer
    answer = pc.createAnswer()
    pc.setLocalDescription(answer)
    return jsonify({'sdp' : pc.localDescription.sdp})

if __name__ == "__main__":
    app.run()
