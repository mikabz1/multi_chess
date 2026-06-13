from datetime import datetime
import uuid
import chess
from app.extensions import db


class Game(db.Model):
    __tablename__ = "games"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    white_player_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    black_player_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    status = db.Column(db.String(20), nullable=False, default="waiting")
    current_fen = db.Column(db.Text, nullable=False, default=chess.STARTING_FEN)
    result = db.Column(db.String(30), nullable=True)
    winner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    invite_token = db.Column(db.String(64), nullable=False, unique=True, default=lambda: uuid.uuid4().hex)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    started_at = db.Column(db.DateTime, nullable=True)
    finished_at = db.Column(db.DateTime, nullable=True)

    white_player = db.relationship("User", foreign_keys=[white_player_id])
    black_player = db.relationship("User", foreign_keys=[black_player_id])
    winner = db.relationship("User", foreign_keys=[winner_id])

    def to_dict(self):
        board = chess.Board(self.current_fen)
        return {
            "id": self.id,
            "white_player": self.white_player.to_dict() if self.white_player else None,
            "black_player": self.black_player.to_dict() if self.black_player else None,
            "status": self.status,
            "current_fen": self.current_fen,
            "turn": "white" if board.turn == chess.WHITE else "black",
            "result": self.result,
            "winner_id": self.winner_id,
            "invite_token": self.invite_token,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
        }
