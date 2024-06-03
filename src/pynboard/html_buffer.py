import warnings
from typing import List
from typing import Optional
from typing import Union

import numpy as np
import pandas as pd
import pandas.io.formats.style
import plotly.graph_objects as go
import plotly.io as pio


class HtmlBuffer:
    _buffer_data: List[str]
    _rendered: Optional[str] = None

    def __init__(self):
        self._buffer_data = []

    def append(self, obj, **kwargs) -> None:
        html = _obj_to_html(obj, **kwargs)
        self._buffer_data.append(html)

    def render(self):
        self._rendered = "\n<br>\n".join(self._buffer_data)

    @property
    def rendered(self):
        return self._rendered

    def reset(self):
        self._buffer_data = []
        self._rendered = None


# region html conversion

def _obj_to_html(obj, **kwargs) -> str:
    if isinstance(obj, (list, tuple)):
        out_html = _obj_grid_to_html(obj, **kwargs)
    else:
        out_html = _obj_single_to_html(obj, **kwargs)
    return out_html


def _obj_single_to_html(obj, **kwargs):
    if isinstance(obj, go.Figure):
        html0 = pio.to_html(obj, full_html=False)
    elif isinstance(obj, pandas.io.formats.style.Styler):
        html0 = obj.to_html()
    elif isinstance(obj, (pd.DataFrame, pd.Series)):
        if isinstance(obj, pd.Series):
            obj = obj.to_frame()
        html0 = _generate_frame_style(obj, index=kwargs.get("index", True)).to_html()
    elif isinstance(obj, str):
        html0 = obj
    else:
        raise TypeError("unexpected object type {}".format(type(obj)))
    return html0


def _obj_grid_to_html(objs, **kwargs):
    html_out_list = ["<table>"]
    if (len(objs) > 0) and (not isinstance(objs[0], (list, tuple))):
        objs = [objs]
    for obj_row in objs:
        html_out_list.append("<tr>")
        for obj in obj_row:
            html0 = _obj_single_to_html(obj, **kwargs)
            html_out_list.append(f"<td>{html0}</td>")
        html_out_list.append("</tr>")

    html_out_list.append("</table>")

    out = "\n".join(html_out_list)
    return out


# endregion

# region data frame rendering

_FONT_FAM = 'menlo,consolas,monospace'
_FONT_SZ = "0.8em"

_HEADER_COLOR = "rgba(214, 234, 248, 1)"

_DATA_FRAME_STYLES = [
    # Table styles
    {
        "selector": "table",
        "props": [
            ("font-family", _FONT_FAM),
            ("font-size", _FONT_SZ),
            ("width", "100%"),
            ("border-collapse", "collapse"),
        ],
    },
    # Header row style
    {"selector": "thead", "props": [("background-color", _HEADER_COLOR)]},
    # Header cell style
    {
        "selector": "th",
        "props": [
            ("font-weight", "700"),
            ("padding", "10px"),
            ("font-family", _FONT_FAM),
            ("font-size", _FONT_SZ),
            ("text-align", "right"),
            # sticky header
            ("position", "sticky"),
            ("top", "0px"),
            ("background-color", _HEADER_COLOR),
        ],
    },
    # Body cell style
    {
        "selector": "td",
        "props": [
            ("padding", "10px"),
            ("font-family", _FONT_FAM),
            ("font-size", _FONT_SZ),
            # ("border-bottom", "1px solid #dddddd"),
            ("text-align", "right"),
        ],
    },
    # zebra
    {"selector": "tr:nth-child(even)", "props": [("background-color", "#F0F0F0")]},
    # hover effect
    {"selector": "tr:hover", "props": [("background-color", "lightyellow")]},
]


def _get_numeric_col_indices(df_in):
    is_numeric = [pd.api.types.is_numeric_dtype(df_in[col]) for col in df_in.columns]
    numeric_indices = [index for index, is_num in enumerate(is_numeric) if is_num]
    return numeric_indices


def _get_default_numeric_col_display_precision(data_in):
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=RuntimeWarning)

        # TODO: comment on the display precision heuristic
        max_prec = 4
        mad = abs(data_in - data_in.median()).median()
        prec_mad = np.floor(np.log10(mad)) - 1
        prec_std = np.floor(np.log10(data_in.std())) - 1
        prec_mean = np.floor(np.log10(data_in.mean())) - 1
        prec = (
            pd.concat([prec_mad, prec_std, prec_mean], axis=1)
            .replace([np.inf, -np.inf], np.nan)
            .bfill(axis=1)
            .fillna(0)
        )
        out = np.clip((prec.iloc[:, 0] * -1), a_min=0, a_max=max_prec).astype(int).values
        return out


def _is_date_only_dt_column(col: Union[pd.Series, pd.Index]) -> bool:
    is_series = isinstance(col, pd.Series)
    if is_series:
        floored = col.dt.floor("D")
    else:
        floored = col.floor("D")
    deltas = col - floored

    if is_series:
        secs = deltas.dt.total_seconds()
    else:
        secs = deltas.total_seconds()

    out = np.allclose(secs, 0)
    return out


def _date_only_dt_formatter(x):
    out = x.strftime("%Y-%m-%d")
    return out


def _apply_sticky_headers(style):
    style.set_sticky(axis=1)
    for style_i in style.table_styles:
        sel = style_i.get("selector")
        if sel and sel.startswith("thead"):
            props = style_i["props"]
            props = [p_i for p_i in props if p_i[0] != "background-color"]
            props.append(("background-color", _HEADER_COLOR))
            style_i["props"] = props

    return style



def _generate_frame_style(df_in, index=None):
    if index is None:
        index = True

    style_out = df_in.style.set_table_styles(_DATA_FRAME_STYLES)

    # precision
    idx_num_cols = _get_numeric_col_indices(df_in)
    prec = _get_default_numeric_col_display_precision(df_in.iloc[:, idx_num_cols])
    num_cols = df_in.columns[idx_num_cols]
    for i0, c0 in enumerate(num_cols):
        style_out.format(precision=prec[i0], subset=c0, thousands=",")

    # datetime
    dt_cols = [c for c in df_in if pd.api.types.is_datetime64_any_dtype(df_in[c])]
    date_only_dt_cols = [c for c in dt_cols if _is_date_only_dt_column(df_in[c])]
    style_out.format(formatter=_date_only_dt_formatter, subset=date_only_dt_cols)

    for lvl in range(df_in.index.nlevels):
        idx_vals = df_in.index.get_level_values(lvl)
        if pd.api.types.is_datetime64_any_dtype(idx_vals):
            if _is_date_only_dt_column(idx_vals):
                style_out.format_index(formatter=_date_only_dt_formatter, level=lvl)

    _apply_sticky_headers(style_out)

    # index display
    if not index:
        style_out.hide()

    return style_out

# endregion
