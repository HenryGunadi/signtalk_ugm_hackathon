from flask import Blueprint, jsonify, request
from supabase import Client
from flask_jwt_extended import create_access_token, get_jwt_identity

def create_index_bp(supabase: Client):
    index_bp = Blueprint('dashboard_bp', __name__)
    
    @index_bp.route("/create_room", methods=["POST"])
    def create_room():
        try:
            data: dict = request.get_json()
            room_name = data.get("name")
            
            if not room_name:
                return jsonify({"error": "Room name is required"}), 400
            
            response = supabase.table("meeting_rooms").insert({"name": data.get("name")}).execute()
            
            return jsonify({"success": True, "response" : response}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    @index_bp.route("/join_room", methods=["POST"])
    def join_room():
        try:
            data: dict = request.get_json()
            room_id: int = data.get("room_id")
            
            if not room_id:
                return jsonify({"error": "Missing room id"}), 400
            
            response: dict = (
                supabase.table("meeting_rooms")
                .select("*")
                .eq("id", room_id).execute()
            )
            
            if len(response.get("data")) == 0:
                return jsonify({"error": "Room id not found"}), 400
            
            response: dict = (
                supabase.table("users")
                .update({"room_id": room_id})
                .eq("id", data.get("user_id"))
                .execute()
            )
            
            # User will be redirected from client side
            return jsonify({"success": True}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    @index_bp.route("/get_user", methods=["POST"])
    def get_user():
        try:
            pass
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    return index_bp