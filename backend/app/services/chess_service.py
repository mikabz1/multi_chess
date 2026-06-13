from datetime import datetime
import chess
from app.extensions import db
from app.models.game import Game
from app.models.move import Move
from app.models.user import User


class ChessServiceError(Exception):
    pass


def get_player_color(game: Game, user_id: int) -> str | None:
    if game.white_player_id == user_id:
        return "white"
    if game.black_player_id == user_id:
        return "black"
    return None


def apply_move(game: Game, user_id: int, uci_move: str) -> dict:
    if game.status != "active":
        raise ChessServiceError("Game is not active")

    player_color = get_player_color(game, user_id)
    if player_color is None:
        raise ChessServiceError("You are not a player in this game")

    board = chess.Board(game.current_fen)
    expected_color = "white" if board.turn == chess.WHITE else "black"
    if player_color != expected_color:
        raise ChessServiceError("It is not your turn")

    try:
        move = chess.Move.from_uci(uci_move)
    except ValueError:
        raise ChessServiceError("Invalid move format")

    if move not in board.legal_moves:
        raise ChessServiceError("Illegal move")

    san_move = board.san(move)
    board.push(move)

    move_count = Move.query.filter_by(game_id=game.id).count() + 1
    move_row = Move(
        game_id=game.id,
        player_id=user_id,
        move_number=move_count,
        uci_move=uci_move,
        san_move=san_move,
        fen_after=board.fen(),
    )
    db.session.add(move_row)

    game.current_fen = board.fen()

    game_over = False
    if board.is_checkmate():
        game_over = True
        game.status = "finished"
        game.finished_at = datetime.utcnow()
        game.winner_id = user_id
        game.result = "white_win" if player_color == "white" else "black_win"
        update_player_stats(game, winner_id=user_id, draw=False)
    elif board.is_stalemate() or board.is_insufficient_material() or board.can_claim_fifty_moves() or board.can_claim_threefold_repetition():
        game_over = True
        game.status = "finished"
        game.finished_at = datetime.utcnow()
        game.result = "draw"
        update_player_stats(game, winner_id=None, draw=True)

    db.session.commit()

    return {
        "game": game.to_dict(),
        "move": move_row.to_dict(),
        "game_over": game_over,
    }


def resign_game(game: Game, user_id: int) -> dict:
    player_color = get_player_color(game, user_id)
    if player_color is None:
        raise ChessServiceError("You are not a player in this game")
    if game.status != "active":
        raise ChessServiceError("Game is not active")

    winner_id = game.black_player_id if player_color == "white" else game.white_player_id
    game.status = "finished"
    game.finished_at = datetime.utcnow()
    game.winner_id = winner_id
    game.result = "black_win" if player_color == "white" else "white_win"
    update_player_stats(game, winner_id=winner_id, draw=False)
    db.session.commit()
    return game.to_dict()


def update_player_stats(game: Game, winner_id: int | None, draw: bool) -> None:
    players = [game.white_player_id, game.black_player_id]
    users = {u.id: u for u in User.query.filter(User.id.in_(players)).all()}

    if draw:
        for user in users.values():
            user.draws += 1
        return

    for player_id, user in users.items():
        if player_id == winner_id:
            user.wins += 1
            user.rating += 10
        else:
            user.losses += 1
            user.rating = max(100, user.rating - 10)
