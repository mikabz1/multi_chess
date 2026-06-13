from flask import request
from flask_jwt_extended import decode_token
from flask_socketio import emit, join_room, leave_room
from app.extensions import socketio
from app.models.game import Game
from app.services.chess_service import apply_move, get_player_color, ChessServiceError


def get_user_id_from_auth(auth):
    token = (auth or {}).get("token")
    if not token:
        return None
    try:
        decoded = decode_token(token)
        return int(decoded["sub"])
    except Exception:
        return None


@socketio.on("join_game")
def handle_join_game(data):
    user_id = get_user_id_from_auth(data)
    game_id = data.get("game_id")
    game = Game.query.get(game_id)

    if not user_id or not game:
        emit("error_message", {"error": "Unauthorized or game not found"})
        return

    if user_id not in [game.white_player_id, game.black_player_id]:
        emit("error_message", {"error": "You are not a player in this game"})
        return

    room = f"game:{game_id}"
    join_room(room)
    emit("game_state", {"game": game.to_dict(), "your_color": get_player_color(game, user_id)})
    emit("player_joined", {"user_id": user_id}, to=room, include_self=False)


@socketio.on("leave_game")
def handle_leave_game(data):
    game_id = data.get("game_id")
    if game_id:
        leave_room(f"game:{game_id}")


@socketio.on("make_move")
def handle_make_move(data):
    user_id = get_user_id_from_auth(data)
    game_id = data.get("game_id")
    uci_move = data.get("move")
    game = Game.query.get(game_id)

    if not user_id or not game:
        emit("invalid_move", {"error": "Unauthorized or game not found"})
        return

    try:
        result = apply_move(game, user_id, uci_move)
        emit("move_made", result, to=f"game:{game_id}")
        if result["game_over"]:
            emit("game_over", {"game": result["game"]}, to=f"game:{game_id}")
    except ChessServiceError as exc:
        emit("invalid_move", {"error": str(exc)})
