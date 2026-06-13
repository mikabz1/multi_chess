from flask import Blueprint, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.extensions import db
from app.models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    data = request.get_json() or {}
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if len(username) < 3:
        return {"error": "Username must be at least 3 characters"}, 400
    if "@" not in email:
        return {"error": "Invalid email"}, 400
    if len(password) < 6:
        return {"error": "Password must be at least 6 characters"}, 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return {"error": "Username or email already exists"}, 409

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return {"access_token": token, "user": user.to_dict()}, 201


@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    username_or_email = (data.get("username_or_email") or "").strip()
    password = data.get("password") or ""

    user = User.query.filter(
        (User.username == username_or_email) | (User.email == username_or_email.lower())
    ).first()

    if not user or not user.check_password(password):
        return {"error": "Invalid credentials"}, 401

    token = create_access_token(identity=str(user.id))
    return {"access_token": token, "user": user.to_dict()}


@auth_bp.get("/me")
@jwt_required()
def me():
    user = User.query.get(int(get_jwt_identity()))
    return {"user": user.to_dict()}
