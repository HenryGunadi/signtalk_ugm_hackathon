from flask import Flask, request, jsonify
from aiortc import RTCPeerConnection, MediaStreamTrack
from flask_sockets import Sockets

app = Flask(__name__)
sockets = Sockets(app)

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
