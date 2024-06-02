from typing import Optional

from core import Board
from utils import create_default_board

_active_board: Optional[Board] = None

__all__ = [
    "append",
    "render",
    "render_obj",
    "reset",
]


def get_active_board() -> Board:
    global _active_board
    if _active_board is None:
        _active_board = create_default_board()

    return _active_board


def set_active_board(board: Board) -> None:
    global _active_board
    _active_board = board


def append(obj, **kwargs) -> None:
    board = get_active_board()
    board.append(obj, **kwargs)


def render():
    board = get_active_board()
    board.render()


def render_obj(obj, **kwargs) -> None:
    board = get_active_board()
    board.append(obj, **kwargs)
    board.render()


def reset():
    get_active_board().reset()
