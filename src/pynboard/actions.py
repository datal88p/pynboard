import tempfile
import webbrowser
from pathlib import Path
from typing import Optional

from pynboard.core import Buffer


def _gen_tempfile(suffix: Optional[str] = None):
    temp_dir = Path.home() / "tmp" / "pynboard"
    if not temp_dir.exists():
        temp_dir.mkdir(parents=True)

    out = tempfile.NamedTemporaryFile(
        mode="w", dir=temp_dir, suffix=suffix, encoding="utf-8", delete=False
    )
    return out


_META_KEY_SAVED_BUFFER_PATH = "saved_buffer_path"


def dump_rendered_to_html_file(buffer: Buffer, meta: dict, path=None) -> None:
    # path is provided
    if path is not None:
        path = Path(path)
        if not path.parent.exists():
            path.parent.mkdir(parents=True)

        with open(path, "w", encoding="utf-8") as f:
            f.write(buffer.rendered)
    # otherwise use a tempfile
    else:
        suffix = ".html"
        with _gen_tempfile(suffix=suffix) as f:
            f.write(buffer.rendered)
            path = Path(f.name)

    meta[_META_KEY_SAVED_BUFFER_PATH] = path


def open_saved_buffer_in_browser(buffer: Buffer, meta: dict) -> None:
    path = meta[_META_KEY_SAVED_BUFFER_PATH]
    webbrowser.open(f"file:{path}")


def reset_buffer(buffer: Buffer, meta: dict) -> None:
    buffer.reset()
