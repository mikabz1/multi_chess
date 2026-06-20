from datetime import datetime
from flask_jwt_extended import decode_token
from flask_socketio import emit
from app.extensions import socketio, db
from app.models.game import Game

# [(user_id, sid)]
_queue = []


def _get_user_id(data):
    try:
        return int(decode_token((data or {}).get("token", ""))["sub"])
    except Exception:
        return None


def _remove_from_queue(user_id=None, sid=None):
    global _queue
    _queue = [e for e in _queue if e[0] != user_id and e[1] != sid]


@socketio.on("join_queue")
def handle_join_queue(data):
    from flask_socketio import join_room
    user_id = _get_user_id(data)
    if not user_id:
        emit("queue_error", {"error": "Unauthorized"})
        return

    from flask import request
    sid = request.sid

    # avoid duplicates
    if any(e[0] == user_id for e in _queue):
        emit("queue_joined", {"position": len(_queue)})
        return

    _queue.append((user_id, sid))

    if len(_queue) >= 2:
        (id_a, sid_a), (id_b, sid_b) = _queue.pop(0), _queue.pop(0)

        game = Game(white_player_id=id_a, black_player_id=id_b,
                    status="active", started_at=datetime.utcnow())
        db.session.add(game)
        db.session.commit()

        emit("match_found", {"game_id": game.id, "your_color": "white"}, to=sid_a)
        emit("match_found", {"game_id": game.id, "your_color": "black"}, to=sid_b)
    else:
        emit("queue_joined", {"position": 1})


@socketio.on("leave_queue")
def handle_leave_queue(data):
    from flask import request
    user_id = _get_user_id(data)
    _remove_from_queue(user_id=user_id, sid=request.sid)
    emit("queue_left", {})


@socketio.on("disconnect")
def handle_disconnect():
    from flask import request
    _remove_from_queue(sid=request.sid)
