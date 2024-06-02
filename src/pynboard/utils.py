from actions import dump_rendered_to_tempfile
from actions import open_saved_buffer_in_browser
from actions import reset_buffer
from core import Board
from html_buffer import HtmlBuffer


def create_default_board():
    buffer = HtmlBuffer()
    pb = Board(buffer)
    pb.set_post_render_actions(actions=[
        dump_rendered_to_tempfile,
        open_saved_buffer_in_browser,
        reset_buffer,
    ])

