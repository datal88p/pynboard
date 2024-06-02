import tempfile
import webbrowser
from pathlib import Path
from typing import Optional

from core import Buffer
from html_buffer import HtmlBuffer


def _gen_tempfile(suffix: Optional[str] = None):
    temp_dir = Path.home() / "tmp" / "pynboard"
    if not temp_dir.exists():
        temp_dir.mkdir(parents=True)

    out = tempfile.NamedTemporaryFile(
        mode="w", dir=temp_dir, suffix=suffix, encoding="utf-8", delete=False
    )
    return out


_META_KEY_SAVED_BUFFER_PATH = "saved_buffer_path"


def dump_rendered_to_tempfile(buffer: Buffer, meta: dict) -> None:
    suffix = None
    if isinstance(buffer, HtmlBuffer):
        suffix = ".html"

    with _gen_tempfile(suffix=suffix) as f:
        f.write(buffer.rendered)
        meta[_META_KEY_SAVED_BUFFER_PATH] = Path(f.name)


def open_saved_buffer_in_browser(buffer: Buffer, meta: dict) -> None:
    path = meta[_META_KEY_SAVED_BUFFER_PATH]
    webbrowser.open(f"file:{path}")


def reset_buffer(buffer: Buffer, meta: dict) -> None:
    buffer.reset()
