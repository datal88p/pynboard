from functools import partial
from pathlib import Path
from typing import Iterable
from typing import Optional
from typing import Union

from pynboard import actions
from pynboard.core import Board
from pynboard.core import PostRenderAction
from pynboard.html_buffer import HtmlBuffer


def create_default_board() -> Board:
    buffer = HtmlBuffer()
    board = Board(buffer)
    actions = action_sequence_html_file(file_path=None, open_file=True)
    board.set_post_render_actions(actions=actions)
    return board


def init_html_board(
        file_path=Optional[Union[Path, str]],
        open_file: bool = False,
        reset_on_render: bool = True,
        set_active: bool = True,
) -> Board:
    board = create_default_board()
    actions = action_sequence_html_file(
        file_path=file_path,
        open_file=open_file,
        reset_buffer=reset_on_render
    )
    board.set_post_render_actions(actions=actions)

    if set_active:
        # prevent circular import
        from pynboard import set_active_board
        set_active_board(board)

    return board


def action_sequence_html_file(file_path=None, open_file=False, reset_buffer=True) -> Iterable[PostRenderAction]:
    out = []

    save_action = partial(actions.dump_rendered_to_html_file, path=file_path)
    out.append(save_action)

    if open_file:
        out.append(actions.open_saved_buffer_in_browser)

    if reset_buffer:
        out.append(actions.reset_buffer)

    return out
