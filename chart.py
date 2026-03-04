from standard import *
import plotly.graph_objects as go


def chart(logs: pd.DataFrame):

    cols = ["schedule", "hour", "load", "id", "mc", "type", "dispatch"]
    df = logs[cols].copy()

    df = logs.copy()  # schedule,hour,load,id,mc,type,dispatch
    df["t"] = (df["schedule"] - 1) * 24 + df["hour"]

    # 1) Per generator: mc and type (assumed constant per id)
    gen_info = df.groupby("id", as_index=False).agg({"mc": "mean", "type": "first"})

    # 2) Order generators by mc (cheapest first)
    gen_info = gen_info.sort_values("mc")
    # gen_order = gen_info["id"].tolist()

    fig = go.Figure()

    for _, row in gen_info.iterrows():
        gen_id = row["id"]
        gen_type = row["type"]
        g = df[df["id"] == gen_id].sort_values("t")
        fig.add_trace(
            go.Scatter(
                x=g["t"],
                y=g["dispatch"],
                mode="lines",
                stackgroup="one",
                name=f"{gen_type} {gen_id}",  # e.g. "nuclear 25"
                line=dict(width=0.5),
            )
        )

    # Load line
    load = df.drop_duplicates("t")[["t", "load"]].sort_values("t")
    fig.add_trace(
        go.Scatter(
            x=load["t"],
            y=load["load"],
            mode="lines",
            name="Load",
            line=dict(color="black", width=2),
            fill=None,
            stackgroup=None,
        )
    )

    fig.update_layout(
        xaxis_title="Hour",
        yaxis_title="Power (MW)",
    )

    fig.show()


PASTEL_RAINBOW = [
    "#FFB3B3",  # pastel red
    "#FFD9B3",  # pastel orange
    "#FFFBB3",  # pastel yellow
    "#B3FFB3",  # pastel green
    "#B3FFFF",  # pastel cyan
    "#B3D9FF",  # pastel blue
    "#D9B3FF",  # pastel violet
]


def _to_grayscale(hex_color):
    """Convert a hex color to its grayscale equivalent."""
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    # luminance-weighted grayscale
    gray = int(0.299 * r + 0.587 * g + 0.114 * b)
    return f"#{gray:02X}{gray:02X}{gray:02X}"


def chart_by_type(logs: pd.DataFrame, highlight_ids: list = None):

    type_colors = {
        "nuclear": "#72DCC6",
        "solar": "#FDFD96",
        "wind": "#9BCBFB",
        "gas": "#FF6961",
        "coal": "#444141",
        "hydro": "#307CC7",
        "imports": "#C8A8F8",
    }

    cols = ["schedule", "hour", "load", "id", "mc", "type", "dispatch"]
    df = logs[cols].copy()
    df["t"] = (df["schedule"] - 1) * 24 + df["hour"]

    gen_info = df.groupby("id", as_index=False).agg({"mc": "mean", "type": "first"})
    gen_info = gen_info.sort_values("mc")

    type_counts = gen_info["type"].value_counts().to_dict()

    fig = go.Figure()

    rainbow_idx = 0

    for _, row in gen_info.iterrows():
        gen_id = row["id"]
        gen_type = row["type"]
        g = df[df["id"] == gen_id].sort_values("t")

        # Determine the "true" color first
        if type_counts.get(gen_type, 0) > 1:
            true_color = PASTEL_RAINBOW[rainbow_idx % len(PASTEL_RAINBOW)]
            rainbow_idx += 1
            outline = "black"
        else:
            true_color = type_colors.get(gen_type, "#C8C8C8")
            outline = true_color

        # If highlight_ids is set and this id is NOT in it, drain to grayscale
        if highlight_ids is not None and gen_id not in highlight_ids:
            fill_color = _to_grayscale(true_color)
            line_color = _to_grayscale(outline)
        else:
            fill_color = true_color
            line_color = outline

        fig.add_trace(
            go.Scatter(
                x=g["t"],
                y=g["dispatch"],
                mode="lines",
                stackgroup="one",
                name=f"{gen_type} {gen_id}",
                line=dict(width=0.5, color=line_color),
                fillcolor=fill_color,
            )
        )

    # Load line
    load = df.drop_duplicates("t")[["t", "load"]].sort_values("t")
    fig.add_trace(
        go.Scatter(
            x=load["t"],
            y=load["load"],
            mode="lines",
            name="Load",
            line=dict(color="black", width=2),
            fill=None,
            stackgroup=None,
        )
    )

    fig.update_layout(
        xaxis_title="Hour",
        yaxis_title="Power (MW)",
    )

    fig.show()
