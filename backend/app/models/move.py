from datetime import datetime
from app.extensions import db


class Move(db.Model):
    __tablename__ = "moves"

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.String(36), db.ForeignKey("games.id"), nullable=False, index=True)
    player_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    move_number = db.Column(db.Integer, nullable=False)
    uci_move = db.Column(db.String(10), nullable=False)
    san_move = db.Column(db.String(20), nullable=False)
    fen_after = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "game_id": self.game_id,
            "player_id": self.player_id,
            "move_number": self.move_number,
            "uci_move": self.uci_move,
            "san_move": self.san_move,
            "fen_after": self.fen_after,
            "created_at": self.created_at.isoformat(),
        }
