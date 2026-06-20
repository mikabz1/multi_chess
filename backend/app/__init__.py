import os
import time
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

from app.extensions import db, migrate, jwt, socketio


def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        "postgresql://chess:chess@localhost:5432/chess_db",
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    CORS(app, resources={r"/api/*": {"origins": os.getenv("CORS_ORIGINS", "*")}})

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    socketio.init_app(app)

    from app.models import user, game, move, chat_message  # noqa: F401

    from app.routes.auth_routes import auth_bp
    from app.routes.game_routes import games_bp
    from app.routes.user_routes import users_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(games_bp, url_prefix="/api/games")
    app.register_blueprint(users_bp, url_prefix="/api/users")

    from app.sockets import game_socket, chat_socket, matchmaking_socket  # noqa: F401

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    with app.app_context():
        max_attempts = int(os.getenv("DB_INIT_MAX_ATTEMPTS", "30"))
        delay_seconds = int(os.getenv("DB_INIT_RETRY_DELAY_SECONDS", "2"))

        for attempt in range(1, max_attempts + 1):
            try:
                db.create_all()
                break
            except Exception as exc:
                if attempt == max_attempts:
                    raise
                print(
                    f"Database is not ready yet. "
                    f"Retrying {attempt}/{max_attempts} in {delay_seconds}s... "
                    f"Error: {exc}",
                    flush=True,
                )
                time.sleep(delay_seconds)

    return app
