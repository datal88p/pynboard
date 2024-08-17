from functools import partial
from pathlib import Path
from typing import Iterable
from typing import Optional
from typing import Sequence
from typing import Union

from pynboard import actions
from pynboard.core import Board
from pynboard.core import PostRenderAction
from pynboard.display_properties import DisplayPropertiesDataFrame
from pynboard.display_properties import DisplayPropertiesStr
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


def dprops_df(
        index: Optional[bool] = None,
        title: Optional[str] = None,
        bg_grad_subset: Optional[Union[str, Sequence[str]]] = None,
        bg_grad_cmap: Optional[object] = None,
        bg_grad_axis: Optional[int] = 0,
        bg_grad_reversed: bool = False,
        bg_grad_vmin: Optional[float] = None,
        bg_grad_vmax: Optional[float] = None,
) -> DisplayPropertiesDataFrame:
    out = DisplayPropertiesDataFrame(
        index=index,
        title=title,
        bg_grad_subset=bg_grad_subset,
        bg_grad_cmap=bg_grad_cmap,
        bg_grad_axis=bg_grad_axis,
        bg_grad_reversed=bg_grad_reversed,
        bg_grad_vmin=bg_grad_vmin,
        bg_grad_vmax=bg_grad_vmax,
    )
    return out


def dprops_str(is_markdown: bool = True) -> DisplayPropertiesStr:
    out = DisplayPropertiesStr(
        is_markdown=is_markdown,
    )
    return out
