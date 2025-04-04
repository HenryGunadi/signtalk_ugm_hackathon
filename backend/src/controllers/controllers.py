from flask import Blueprint, jsonify, request, render_template
from supabase import Client
from flask_jwt_extended import create_access_token, get_jwt_identity, set_refresh_cookies, set_access_cookies, create_refresh_token, unset_jwt_cookies, jwt_required
from utils import validators
from marshmallow import ValidationError
from flask_bcrypt import Bcrypt
from models import models
from datetime import timedelta

def create_index_bp(supabase: Client):
    index_bp = Blueprint('dashboard_bp', __name__, url_prefix="/")
    
    @index_bp.route("/", methods=["GET"])
    # @jwt_required()
    def index():
        try:
            response = supabase.table("meeting_rooms").select("name").eq("name", "testing").execute()
            
            data = response.data

            return render_template("index.html", meetings=data)
        except Exception as e:
            return jsonify({"type": "error", "message": str(e)}), 500
        
    
    @index_bp.route("/create_room", methods=["POST"])
    @jwt_required()
    def create_room():
        try:
            data: dict = request.get_json()
            room_name = data.get("name")
            
            if not room_name:
                return jsonify({"error": "Room name is required"}), 400
            
            response = supabase.table("meeting_rooms").insert({"name": data.get("name")}).execute()

            if response.data:
                room_id = response.data[0]["id"]
                return jsonify({"success": True, "room_id" : room_id}), 200
            else:
                return jsonify({"error": "Failed to insert room"}), 500
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    @index_bp.route("/join_room", methods=["POST"])
    @jwt_required()
    def join_room():
        try:
            data: dict = request.get_json()
            room_id: int = data.get("room_id")
            
            if not room_id:
                return jsonify({"error": "Missing room id"}), 400
            
            response: dict = (
                supabase.table("meeting_rooms")
                .select("*")
                .eq("id", room_id)
                .single()
                .execute()
            ).data
            
            if not response:
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
        
    # @index_bp.route("/get_user", methods=["POST"])
    # def get_user():
    #     try:
            
    #     except Exception as e:
    #         return jsonify({"error": str(e)}), 500
        
    return index_bp

def create_auth_bp(supabase: Client):
    auth_bp = Blueprint("auth_bp", __name__)
    
    @auth_bp.route("/register", methods=["POST"])
    def register():
        try:
            # validation
            registerSchema = validators.RegisterSchema()
            data: dict = registerSchema.load(request.get_json())
            
            # hash password
            data["password"] = Bcrypt.generate_password_hash(data["password"]).decode("utf-8")
            
            # create user in db
            _ = (
                supabase.table("users")
                .insert(data)
                .execute()
            )
            
            return jsonify({
                    "success": True, 
                })
        except ValidationError as e:
            return jsonify({"error" : e.messages}), 400
        except Exception as e:
            return jsonify({"error" : str(e)}), 500
    
    @auth_bp.route("/login", methods=["POST"])
    def login():
        try:
            # validation
            loginSchema = validators.LoginSchema()
            data: dict = loginSchema.load(request.get_json())
            
            # get user from db
            response: dict = (
                supabase.table("users")
                .select("*")
                .eq("email", data.get("email"))
                .maybe_single()
                .execute()
            ).data
            
            if not response:
                return jsonify({"error": "Invalid credentials!"}), 400
            
            # create user instance
            user = models.User(name=response.get("name"),
                               email=response.get("email"),
                               password=response.get("password")) # <-- hashed password
            
            # check password
            is_valid = Bcrypt.check_password_hash(response.get("password"), data.get("password"))
            
            if not is_valid:
                return jsonify({"error": "Invalid credentials!"}), 400
            
            # create jwt
            access_token = create_access_token(identity=response.get("email"), expires_delta=timedelta(minutes=15), fresh=True)

            refresh_token = create_refresh_token(
                identity=response.get("email"),
                expires_delta=timedelta(hours=2)
            )
            
            response = jsonify({
                "success": True,
                "user": user.to_dict()
            })
            
            # set tokens into cookies
            set_access_cookies(response, encoded_access_token=access_token)
            set_refresh_cookies(response, encoded_refresh_token=refresh_token)
            
            return response
        except ValidationError as e:
            return jsonify({"error" : e.messages}), 400
        except Exception as e:
            return jsonify({"error" : str(e)}), 500
    
    @auth_bp.route("/logout", methods=["POST"])
    def logout():
        try:
            response = jsonify({"success": True, "message": "Logged out"})
            unset_jwt_cookies(response)  # Clear access and refresh tokens
            return response
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    @auth_bp.route("/refresh_token", methods=["POST"])
    @jwt_required()
    def refresh():
        try:
            current_user = get_jwt_identity()
            new_access_token = create_access_token(identity=current_user, fresh=False, expires_delta=timedelta(minutes=15))

            response = jsonify({"success": True, "message": "Token refreshed!"})
            set_access_cookies(response, encoded_access_token=new_access_token)
            
            return response
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    return auth_bp