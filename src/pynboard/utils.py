from functools import partial
from typing import Iterable

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


def action_sequence_html_file(file_path=None, open_file=False, reset_buffer=True) -> Iterable[PostRenderAction]:
    out = []

    save_action = partial(actions.dump_rendered_to_html_file, path=file_path)
    out.append(save_action)

    if open_file:
        out.append(actions.open_saved_buffer_in_browser)

    if reset_buffer:
        out.append(actions.reset_buffer)

    return out
