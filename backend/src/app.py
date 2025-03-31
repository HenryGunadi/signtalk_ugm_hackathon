from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify, render_template
# from aiortc import RTCPeerConnection, MediaStreamTrack
from flask_sockets import Sockets
from flask_cors import CORS
import os
from supabase import create_client
from flask_jwt_extended import JWTManager, jwt_required

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
secret_key = os.environ.get("SECRET_KEY")
supabase = create_client(url, key)

app = Flask(__name__, template_folder="templates")
# # sockets = Sockets(app)

# cors settings
CORS(
    app,
    resources={r"/*": {"origins": "*"}}, 
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE"],
)

app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_SECRET_KEY"] = ""

# # @sockets.route("/ws")
# # def echo_socket(ws):
# #     while not ws.closed:cls
# #         message = ws.receive()
# #         ws.send(message)

# # @app.route("/offer", methods=["POST"])
# # def handle_offer():
# #     offer = request.json['sdp']
# #     pc = RTCPeerConnection()
# #     pc.setRemoteDescription(offer)

# #     # create an answer
# #     answer = pc.createAnswer()
# #     pc.setLocalDescription(answer)
# #     return jsonify({'sdp' : pc.localDescription.sdp})

@app.route("/")
def index():
    try:
        response = supabase.table("meeting_rooms").select("name").eq("name", "testing").execute()
        
        data = response.data
    except Exception as e:
        return jsonify({"type": "error", "message": str(e)}), 500
    
    return render_template("index.html", meetings=data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000)) 
    app.run(debug=True, port=port, host="0.0.0.0")
