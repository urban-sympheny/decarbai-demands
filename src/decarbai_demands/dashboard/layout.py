"""Dash UI layout: form sections, run button, demand-profiles panel, ranges modal."""

from dash import dcc, html

from decarbai_demands.dashboard.constants import BUILDING_TYPES, CITIES, DEFAULTS, DEMAND_TYPES
from decarbai_demands.dashboard.ranges import TRAINING_RANGES, build_ranges_modal
from decarbai_demands.dashboard.styles import (
    FLEX_ROW,
    HELPER_STYLE,
    INPUT_STYLE,
    LABEL_STYLE,
    SECTION_BOX,
    SECTION_STYLE,
)


def _format_range(lo: float, hi: float) -> str:
    return f"Trained: {lo:g} - {hi:g}"


def create_input_field(
    label: str,
    id: str,
    value: float,
    step: float = 0.1,
    range_key: str | None = None,
) -> html.Div:
    """Labeled numeric input, optionally annotated with its trained-range helper."""
    children: list = [
        html.Label(label, style=LABEL_STYLE),
        dcc.Input(id=id, type="number", value=value, step=step, style=INPUT_STYLE),
    ]
    if range_key is not None:
        lo = TRAINING_RANGES[range_key]["min"]
        hi = TRAINING_RANGES[range_key]["max"]
        children.append(html.Span(_format_range(lo, hi), id=f"{id}_helper", style=HELPER_STYLE))
    return html.Div(children, style={"flex": "1"})


def create_section(title: str) -> html.H4:
    return html.H4(title, style=SECTION_STYLE)


def _header() -> html.Div:
    return html.Div(
        html.H1(
            "DecarbAI Demands Dashboard",
            style={"textAlign": "center", "color": "#fff", "fontSize": "24px", "fontWeight": "500"},
        ),
        style={"backgroundColor": "#3b3b3b", "padding": "16px", "boxShadow": "0 2px 4px rgba(0,0,0,0.1)"},
    )


def _config_header() -> html.Div:
    return html.Div(
        [
            html.H3(
                "Configuration",
                style={"color": "#111827", "fontSize": "15px", "fontWeight": "700", "margin": "0", "letterSpacing": "-0.01em"},
            ),
            html.Button(
                "ⓘ",
                id="ranges_info_btn",
                n_clicks=0,
                title="View training data ranges",
                style={
                    "width": "22px",
                    "height": "22px",
                    "padding": "0",
                    "border": "1px solid #cbd5e1",
                    "borderRadius": "50%",
                    "backgroundColor": "#f1f5f9",
                    "color": "#475569",
                    "fontSize": "13px",
                    "lineHeight": "1",
                    "cursor": "pointer",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center",
                },
            ),
        ],
        style={
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "space-between",
            "marginBottom": "10px",
            "paddingBottom": "6px",
            "borderBottom": "1px solid #e5e7eb",
        },
    )


def _location_and_type_section() -> html.Div:
    return html.Div(
        [
            create_section("Location & Type"),
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("City", style=LABEL_STYLE),
                            dcc.Dropdown(
                                id="city",
                                options=[{"label": c.replace("_", " ").title(), "value": c} for c in CITIES],
                                value="bern",
                                clearable=False,
                                style={"fontSize": "13px"},
                            ),
                        ],
                        style={"flex": "1"},
                    ),
                    html.Div(
                        [
                            html.Label("Building Type", style=LABEL_STYLE),
                            dcc.Dropdown(
                                id="building_type",
                                options=[{"label": bt.title(), "value": bt} for bt in BUILDING_TYPES],
                                value="mfh",
                                clearable=False,
                                style={"fontSize": "13px"},
                            ),
                        ],
                        style={"flex": "1"},
                    ),
                ],
                style=FLEX_ROW,
            ),
            html.Div(
                [
                    html.Label("Demand Types", style=LABEL_STYLE),
                    dcc.Checklist(
                        id="demand_types",
                        options=[{"label": dt.title(), "value": dt} for dt in DEMAND_TYPES],
                        value=["heating", "cooling"],
                        inline=True,
                        style={"display": "flex", "gap": "14px", "flexWrap": "wrap"},
                        inputStyle={"marginRight": "5px", "cursor": "pointer"},
                        labelStyle={
                            "fontSize": "12px",
                            "color": "#3C5137",
                            "cursor": "pointer",
                            "display": "flex",
                            "alignItems": "center",
                        },
                    ),
                ],
                style={"marginTop": "10px"},
            ),
        ],
        style=SECTION_BOX,
    )


def _construction_section() -> html.Div:
    return html.Div(
        [
            create_section("Construction Details"),
            html.Div(
                [
                    create_input_field("Construction Year", "construction_year", DEFAULTS["construction_year"], step=1, range_key="Age"),
                    create_input_field("North Angle [°]", "north_angle", DEFAULTS["north_angle"], range_key="North_Angle"),
                ],
                style=FLEX_ROW,
            ),
        ],
        style=SECTION_BOX,
    )


def _geometry_section() -> html.Div:
    return html.Div(
        [
            create_section("Geometry"),
            html.Div(
                [
                    create_input_field("Length [m]", "length", DEFAULTS["length"], range_key="Length"),
                    create_input_field("Width [m]", "width", DEFAULTS["width"], range_key="Width"),
                ],
                style=FLEX_ROW,
            ),
            html.Div(
                [
                    create_input_field("Floor Height [m]", "floor_height", DEFAULTS["floor_height"], range_key="Height"),
                    create_input_field("Floors", "number_of_floors", DEFAULTS["number_of_floors"], step=1, range_key="Number_of_Floors"),
                ],
                style={**FLEX_ROW, "marginTop": "10px"},
            ),
        ],
        style=SECTION_BOX,
    )


def _wwr_section() -> html.Div:
    return html.Div(
        [
            create_section("Window-to-Wall Ratios"),
            html.Div(
                [
                    create_input_field("North", "nwwr", DEFAULTS["nwwr"], step=0.001, range_key="NWWR"),
                    create_input_field("East", "ewwr", DEFAULTS["ewwr"], step=0.001, range_key="EWWR"),
                ],
                style=FLEX_ROW,
            ),
            html.Div(
                [
                    create_input_field("South", "swwr", DEFAULTS["swwr"], step=0.001, range_key="SWWR"),
                    create_input_field("West", "wwwr", DEFAULTS["wwwr"], step=0.001, range_key="WWWR"),
                ],
                style={**FLEX_ROW, "marginTop": "10px"},
            ),
        ],
        style=SECTION_BOX,
    )


def _u_values_section() -> html.Div:
    return html.Div(
        [
            create_section("U-Values [W/m²K]"),
            html.Div(
                [
                    create_input_field("Ground", "u_ground", DEFAULTS["u_ground"], step=0.001, range_key="U_Ground"),
                    create_input_field("Wall", "u_wall", DEFAULTS["u_wall"], step=0.001, range_key="U_Wall"),
                ],
                style=FLEX_ROW,
            ),
            html.Div(
                [
                    create_input_field("Roof", "u_roof", DEFAULTS["u_roof"], step=0.001, range_key="U_Roof"),
                    create_input_field("Window", "u_window", DEFAULTS["u_window"], step=0.001, range_key="U_Window"),
                ],
                style={**FLEX_ROW, "marginTop": "10px"},
            ),
        ],
        style=SECTION_BOX,
    )


def _run_button() -> html.Button:
    return html.Button(
        "Run Prediction",
        id="run_button",
        n_clicks=0,
        style={
            "width": "100%",
            "padding": "10px",
            "marginTop": "10px",
            "backgroundColor": "#10b981",
            "color": "white",
            "border": "none",
            "borderRadius": "6px",
            "fontSize": "13px",
            "cursor": "pointer",
            "fontWeight": "600",
        },
    )


def _left_panel() -> html.Div:
    return html.Div(
        [
            _config_header(),
            _location_and_type_section(),
            _construction_section(),
            _geometry_section(),
            _wwr_section(),
            _u_values_section(),
            _run_button(),
        ],
        style={
            "width": "360px",
            "padding": "20px",
            "backgroundColor": "#f8fafc",
            "borderRadius": "8px",
            "marginRight": "16px",
            "boxShadow": "0 2px 4px rgba(0,0,0,0.08)",
            "flexShrink": "0",
            "height": "calc(100vh - 88px)",
            "overflowY": "auto",
        },
    )


def _right_panel() -> html.Div:
    return html.Div(
        [
            html.Div(
                [
                    html.H3(
                        "Demand Profiles",
                        style={"color": "#1f2937", "fontSize": "16px", "fontWeight": "600"},
                    ),
                    html.Div(
                        [
                            html.Button("Download CSV", id="download_button", n_clicks=0, style={"display": "none"}),
                            dcc.Download(id="download_csv"),
                        ]
                    ),
                ],
                style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "center",
                    "paddingBottom": "12px",
                    "borderBottom": "1px solid #e5e7eb",
                },
            ),
            html.Div(
                id="status_message",
                style={
                    "padding": "10px",
                    "marginTop": "12px",
                    "backgroundColor": "#f0f9ff",
                    "border": "1px solid #bae6fd",
                    "borderRadius": "4px",
                    "textAlign": "center",
                    "fontSize": "13px",
                    "color": "#0369a1",
                    "fontWeight": "500",
                },
            ),
            dcc.Loading(
                type="circle",
                color="#3b82f6",
                children=[
                    dcc.Graph(
                        id="profile_plot",
                        style={"height": "calc(100vh - 180px)"},
                        config={"displayModeBar": True, "scrollZoom": True, "displaylogo": False},
                    )
                ],
            ),
        ],
        style={
            "flex": "1",
            "padding": "16px",
            "backgroundColor": "#fff",
            "borderRadius": "8px",
            "boxShadow": "0 2px 4px rgba(0,0,0,0.08)",
            "overflow": "hidden",
            "minWidth": "0",
        },
    )


def build_layout() -> html.Div:
    """Top-level Dash layout."""
    return html.Div(
        [
            _header(),
            html.Div(
                [_left_panel(), _right_panel()],
                style={
                    "display": "flex",
                    "padding": "16px",
                    "gap": "16px",
                    "height": "calc(100vh - 56px)",
                    "alignItems": "stretch",
                },
            ),
            build_ranges_modal(),
        ],
        style={
            "fontFamily": "'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
            "backgroundColor": "#f9fafb",
            "height": "100vh",
            "overflow": "hidden",
        },
    )
