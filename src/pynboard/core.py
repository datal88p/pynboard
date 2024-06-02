from typing import Iterable
from typing import Optional
from typing import Protocol


class Buffer(Protocol):
    def append(self, obj, **kwargs) -> None:
        pass

    def render(self):
        pass

    @property
    def rendered(self):
        return None

    def reset(self):
        pass

    def set_post_render_actions(self):
        pass


class PostRenderAction(Protocol):
    def __call__(self, buffer: Buffer, meta: dict) -> None:
        pass


class Board:
    buffer: Buffer
    post_render_actions: Optional[Iterable[PostRenderAction]] = None

    def __init__(self, buffer: Buffer):
        self.buffer = buffer

    def append(self, obj, **kwargs):
        self.buffer.append(obj, **kwargs)

    def render(self):
        self.buffer.render()
        if self.post_render_actions is not None:
            meta = dict()
            for action in self.post_render_actions:
                action(buffer=self.buffer, meta=meta)

    def reset(self):
        self.buffer.reset()

    def set_buffer(self, buffer: Buffer) -> None:
        self.buffer = buffer

    def set_post_render_actions(self, actions: Iterable[PostRenderAction]):
        self.post_render_actions = actions
