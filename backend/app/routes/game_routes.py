from datetime import datetime
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_
from app.extensions import db
from app.models.game import Game
from app.models.move import Move
from app.models.chat_message import ChatMessage
from app.services.chess_service import resign_game, ChessServiceError

games_bp = Blueprint("games", __name__)


@games_bp.post("")
@jwt_required()
def create_game():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    preferred_color = data.get("preferred_color", "white")

    game = Game()
    if preferred_color == "black":
        game.black_player_id = user_id
    else:
        game.white_player_id = user_id

    db.session.add(game)
    db.session.commit()
    return {"game": game.to_dict(), "invite_token": game.invite_token}, 201


@games_bp.post("/join/<invite_token>")
@jwt_required()
def join_game(invite_token):
    user_id = int(get_jwt_identity())
    game = Game.query.filter_by(invite_token=invite_token).first_or_404()

    if game.status == "finished":
        return {"error": "Game already finished"}, 400

    if user_id in [game.white_player_id, game.black_player_id]:
        return {"game": game.to_dict()}

    if game.white_player_id and game.black_player_id:
        return {"error": "Game is already full"}, 409

    if game.white_player_id is None:
        game.white_player_id = user_id
    else:
        game.black_player_id = user_id

    if game.white_player_id and game.black_player_id:
        game.status = "active"
        game.started_at = datetime.utcnow()

    db.session.commit()
    return {"game": game.to_dict()}


@games_bp.get("/<game_id>")
@jwt_required()
def get_game(game_id):
    user_id = int(get_jwt_identity())
    game = Game.query.get_or_404(game_id)
    if user_id not in [game.white_player_id, game.black_player_id]:
        return {"error": "You are not a player in this game"}, 403

    moves = Move.query.filter_by(game_id=game.id).order_by(Move.move_number.asc()).all()
    messages = ChatMessage.query.filter_by(game_id=game.id).order_by(ChatMessage.created_at.asc()).all()
    return {
        "game": game.to_dict(),
        "moves": [m.to_dict() for m in moves],
        "messages": [m.to_dict() for m in messages],
    }


@games_bp.post("/<game_id>/resign")
@jwt_required()
def resign(game_id):
    user_id = int(get_jwt_identity())
    game = Game.query.get_or_404(game_id)
    try:
        updated = resign_game(game, user_id)
        from app.extensions import socketio
        socketio.emit("game_over", {"game": updated, "reason": "resign"}, to=f"game:{game_id}")
        return {"game": updated}
    except ChessServiceError as exc:
        return {"error": str(exc)}, 400


@games_bp.get("")
@jwt_required()
def my_games():
    user_id = int(get_jwt_identity())
    games = Game.query.filter(or_(Game.white_player_id == user_id, Game.black_player_id == user_id))\
        .order_by(Game.created_at.desc()).limit(50).all()
    return {"games": [game.to_dict() for game in games]}
