from flask_socketio import emit
from flask_jwt_extended import decode_token
from app.extensions import db, socketio
from app.models.game import Game
from app.models.chat_message import ChatMessage


def get_user_id_from_auth(auth):
    token = (auth or {}).get("token")
    if not token:
        return None
    try:
        decoded = decode_token(token)
        return int(decoded["sub"])
    except Exception:
        return None


@socketio.on("send_chat_message")
def handle_chat_message(data):
    user_id = get_user_id_from_auth(data)
    game_id = data.get("game_id")
    message = (data.get("message") or "").strip()
    game = Game.query.get(game_id)

    if not user_id or not game:
        emit("error_message", {"error": "Unauthorized or game not found"})
        return
    if user_id not in [game.white_player_id, game.black_player_id]:
        emit("error_message", {"error": "You are not a player in this game"})
        return
    if not message:
        return
    if len(message) > 500:
        emit("error_message", {"error": "Message is too long"})
        return

    row = ChatMessage(game_id=game_id, sender_id=user_id, message=message)
    db.session.add(row)
    db.session.commit()
    emit("chat_message", row.to_dict(), to=f"game:{game_id}")
