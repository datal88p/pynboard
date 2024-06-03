from pynboard.actions import dump_rendered_to_html_tempfile
from pynboard.actions import open_saved_buffer_in_browser
from pynboard.actions import reset_buffer
from pynboard.core import Board
from pynboard.html_buffer import HtmlBuffer


def create_default_board() -> Board:
    buffer = HtmlBuffer()
    board = Board(buffer)
    board.set_post_render_actions(actions=[
        dump_rendered_to_html_tempfile,
        open_saved_buffer_in_browser,
        reset_buffer,
    ])
    return board

