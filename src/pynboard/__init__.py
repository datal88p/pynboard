from typing import Iterable
from typing import Optional

from pynboard.core import Board
from pynboard.core import PostRenderAction
from pynboard.display_properties import DisplayPropertiesType
from pynboard.utils import create_default_board
from pynboard.utils import init_html_board
from pynboard.utils import dprops_df
from pynboard.utils import dprops_str

_active_board: Optional[Board] = None

__all__ = [
    "append",
    "render",
    "render_obj",
    "reset",
    "get_active_board",
    "set_active_board",
    "set_post_render_actions",
    "create_default_board",
    "init_html_board",
    "dprops_df",
    "dprops_str",
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


def append(obj, display_properties: Optional[DisplayPropertiesType] = None) -> None:
    board = get_active_board()
    board.append(obj, display_properties=display_properties)


def render():
    board = get_active_board()
    board.render()


def render_obj(obj, display_properties: Optional[DisplayPropertiesType] = None) -> None:
    board = get_active_board()
    board.append(obj, display_properties=display_properties)
    board.render()


def reset():
    get_active_board().reset()
