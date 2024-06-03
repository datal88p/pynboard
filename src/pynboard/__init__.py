from typing import Iterable
from typing import Optional

from pynboard.core import Board
from pynboard.core import PostRenderAction
from pynboard.utils import create_default_board

_active_board: Optional[Board] = None

__all__ = [
    "append",
    "render",
    "render_obj",
    "reset",
    "get_active_board",
    "set_active_board",
    "set_post_render_actions",
]


def get_active_board() -> Board:
    global _active_board
    if _active_board is None:
        _active_board = create_default_board()

    return _active_board


def set_active_board(board: Board) -> None:
    global _active_board
    _active_board = board


def set_post_render_actions(actions: Iterable[PostRenderAction]) -> None:
    board = get_active_board()
    board.set_post_render_actions(actions)


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
