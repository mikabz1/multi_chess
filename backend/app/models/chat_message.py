from datetime import datetime
from app.extensions import db


class ChatMessage(db.Model):
    __tablename__ = "chat_messages"

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.String(36), db.ForeignKey("games.id"), nullable=False, index=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    sender = db.relationship("User")

    def to_dict(self):
        return {
            "id": self.id,
            "game_id": self.game_id,
            "sender_id": self.sender_id,
            "sender_username": self.sender.username if self.sender else None,
            "message": self.message,
            "created_at": self.created_at.isoformat(),
        }
