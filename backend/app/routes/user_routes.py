from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.game import Game
from sqlalchemy import or_

users_bp = Blueprint("users", __name__)


@users_bp.get("/me/stats")
@jwt_required()
def my_stats():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    games = Game.query.filter(or_(Game.white_player_id == user_id, Game.black_player_id == user_id))\
        .order_by(Game.created_at.desc()).limit(20).all()
    return {
        "user": user.to_dict(),
        "recent_games": [game.to_dict() for game in games],
    }
