from dataclasses import dataclass
from typing import Dict
from typing import Optional
from typing import Sequence
from typing import Union


@dataclass
class DisplayPropertiesDataFrame:
    index: Optional[bool] = None
    title: Optional[str] = None
    precision: Optional[Union[int, Dict[object, int]]] = None
    bg_grad_subset: Optional[Union[str, Sequence[str]]] = None
    bg_grad_cmap: Optional[object] = None
    bg_grad_axis: Optional[int] = 0
    bg_grad_reversed: bool = False
    bg_grad_vmin: Optional[float] = None
    bg_grad_vmax: Optional[float] = None


@dataclass
class DisplayPropertiesStr:
    is_markdown: bool = True


DisplayPropertiesType = Union[
    DisplayPropertiesDataFrame
    | DisplayPropertiesStr
    ]
