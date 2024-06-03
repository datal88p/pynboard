import warnings
from typing import List
from typing import Optional
from typing import Union

import markdown
import numpy as np
import pandas as pd
import pandas.io.formats.style
import plotly.graph_objects as go
import plotly.io as pio
from matplotlib.axes import Axes
from matplotlib.figure import Figure

import io
import base64

class HtmlBuffer:
    _buffer_data: List[str]
    _rendered: Optional[str] = None

    def __init__(self):
        self._buffer_data = []

    def append(self, obj, **kwargs) -> None:
        html = _obj_to_html(obj, **kwargs)
        self._buffer_data.append(html)

    def render(self):
        base = "\n<br>\n".join(self._buffer_data)
        # include style for text rendering
        final = f"{_TEXT_CSS_STYLE}\n\n\n{base}"
        self._rendered = final

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


def _matplotlib_to_html(obj):
    if isinstance(obj, Axes):
        obj = obj.figure

    # figure to buffer
    buf = io.BytesIO()
    obj.savefig(buf, format="png")
    buf.seek(0)
    # buffer to base64 string
    img_base64 = base64.b64encode(buf.read()).decode("utf-8")
    # html element
    html = f"""<img src="data:image/png;base64,{img_base64}">"""

    # png above probably better but will reassess...
    # # figure to buffer
    # buf = io.BytesIO()
    # obj.savefig(buf, format="svg")
    # buf.seek(0)
    # # buffer to base64 string
    # img_svg = buf.getvalue().decode('utf-8')
    # # html element
    # html = f"""<div>{img_svg}</div>"""


    return html

def _obj_single_to_html(obj, **kwargs):
    # plotly
    if isinstance(obj, go.Figure):
        html_out = pio.to_html(obj, full_html=False)
    # matplotlib
    elif isinstance(obj, (Axes, Figure)):
        html_out = _matplotlib_to_html(obj)
    # pandas
    elif isinstance(obj, pandas.io.formats.style.Styler):
        html_out = obj.to_html()
    # pandas
    elif isinstance(obj, (pd.DataFrame, pd.Series)):
        if isinstance(obj, pd.Series):
            obj = obj.to_frame()
        html_out = _generate_frame_style(
            obj, index=kwargs.get("index", True), title=kwargs.get("title")
        ).to_html()
    # text
    elif isinstance(obj, str):
        if kwargs.get("raw_string", False):
            html_out = obj
        else:
            html_out = markdown.markdown(obj)
    else:
        raise TypeError("unexpected object type {}".format(type(obj)))
    return html_out


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
    # title
    {
        "selector": "caption",
        "props": [
            ("font-family", _FONT_FAM),
            ("font-size", "1em"),
            ("text-align", "left"),
            ("font-weight", "700"),
            ("padding-bottom", "1em"),
        ],
    },
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


def _generate_frame_style(df_in, index=None, title=None):
    if index is None:
        index = True

    style_out = df_in.style.set_table_styles(_DATA_FRAME_STYLES)

    # title
    if title is not None:
        style_out.set_caption(title)

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

    # headers
    _apply_sticky_headers(style_out)

    # index display
    if not index:
        style_out.hide()

    return style_out


# endregion

# region CSS for text

_TEXT_CSS_STYLE = """
<style>
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
        line-height: 1.5;
        color: #24292e;
        background-color: #ffffff;
        padding: 20px;
    }

    h1, h2, h3, h4, h5, h6 {
        font-weight: 600;
        margin-top: 24px;
        margin-bottom: 16px;
        border-bottom: 1px solid #eaecef;
        padding-bottom: 0.3em;
    }

    h1 {
        font-size: 2em;
    }

    h2 {
        font-size: 1.5em;
    }

    h3 {
        font-size: 1.25em;
    }

    h4 {
        font-size: 1em;
    }

    h5 {
        font-size: 0.875em;
    }

    h6 {
        font-size: 0.85em;
        color: #6a737d;
    }

    p {
        margin-top: 0;
        margin-bottom: 16px;
    }

    a {
        color: #0366d6;
        text-decoration: none;
    }

    a:hover {
        text-decoration: underline;
    }

    blockquote {
        padding: 0 1em;
        color: #6a737d;
        border-left: 0.25em solid #dfe2e5;
        margin-top: 0;
        margin-bottom: 16px;
    }

    ul, ol {
        padding-left: 2em;
        margin-top: 0;
        margin-bottom: 16px;
    }

    ul {
        list-style-type: disc;
    }

    ol {
        list-style-type: decimal;
    }

    code {
        background-color: rgba(27,31,35,0.05);
        padding: 0.2em 0.4em;
        margin: 0;
        font-size: 85%;
        border-radius: 3px;
        font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
    }

    pre {
        background-color: #f6f8fa;
        padding: 16px;
        overflow: auto;
        line-height: 1.45;
        border-radius: 3px;
        margin-top: 0;
        margin-bottom: 16px;
        border: 1px solid #e1e4e8;
    }

    pre code {
        background: none;
        padding: 0;
        font-size: 100%;
        border: 0;
    }

    table {
        /* width: 100%; */
        overflow: auto;
        margin-top: 0;
        margin-bottom: 16px;
        border-collapse: collapse;
    }

    table th {
        font-weight: 600;
        padding: 6px 13px;
        border: 1px solid #dfe2e5;
        vertical-align: top;
    }

    table td {
        padding: 6px 13px;
        border: 1px solid #dfe2e5;
        vertical-align: top;
    }

    table tr {
        background-color: #ffffff;
        border-top: 1px solid #c6cbd1;
    }

    /*
    table tr:nth-child(2n) {
        background-color: #f6f8fa;
    }
    */

    img {
        max-width: 100%;
        height: auto;
    }
</style>
"""

# endregion
