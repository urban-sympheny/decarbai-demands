"""Training-data envelope for the underlying ML model.

These ranges describe the parameter space the model was trained on. Predictions
remain reliable inside the envelope; outside it the model extrapolates and
confidence drops. The dashboard surfaces them as inline helpers and an info modal.
"""

from dash import html


TRAINING_RANGES: dict[str, dict[str, float]] = {
    "Width": {"min": 5.0, "max": 14.0},
    "Length": {"min": 10.0, "max": 19.0},
    "Height": {"min": 2.5, "max": 3.5},
    "NWWR": {"min": 0.0, "max": 0.75},
    "EWWR": {"min": 0.0, "max": 0.75},
    "SWWR": {"min": 0.0, "max": 0.75},
    "WWWR": {"min": 0.0, "max": 0.75},
    "Age": {"min": 1918.0, "max": 2015.0},
    "North_Angle": {"min": 0.0, "max": 90.0},
    "Number_of_Floors": {"min": 1.0, "max": 4.0},
    "U_Ground": {"min": 0.12, "max": 1.24},
    "U_Wall": {"min": 0.11, "max": 3.06},
    "U_Roof": {"min": 0.11, "max": 1.63},
    "U_Window": {"min": 0.78, "max": 5.67},
    "Footprint [m²]": {"min": 50.0, "max": 266.0},
    "Total Height [m]": {"min": 2.5, "max": 14.0},
    "Volume [m³]": {"min": 125.0, "max": 3724.0},
    "Envelope Area [m²]": {"min": 175.0, "max": 1456.0},
    "Relative Compactness [-]": {"min": 0.65, "max": 1.0},
    "Characteristic Length [m]": {"min": 0.71, "max": 2.56},
    "Average WWR [-]": {"min": 0.0, "max": 0.75},
}

# Maps Dash input id -> key in TRAINING_RANGES
INPUT_TO_RANGE_KEY: dict[str, str] = {
    "length": "Length",
    "width": "Width",
    "floor_height": "Height",
    "number_of_floors": "Number_of_Floors",
    "construction_year": "Age",
    "north_angle": "North_Angle",
    "nwwr": "NWWR",
    "ewwr": "EWWR",
    "swwr": "SWWR",
    "wwwr": "WWWR",
    "u_ground": "U_Ground",
    "u_wall": "U_Wall",
    "u_roof": "U_Roof",
    "u_window": "U_Window",
}

# Computed features the user does not enter directly, but that still bound model validity.
DERIVED_RANGE_KEYS: list[str] = [
    "Footprint [m²]",
    "Total Height [m]",
    "Volume [m³]",
    "Envelope Area [m²]",
    "Relative Compactness [-]",
    "Characteristic Length [m]",
    "Average WWR [-]",
]


MODAL_HIDDEN_STYLE: dict[str, str] = {
    "display": "none",
    "position": "fixed",
    "top": "0",
    "left": "0",
    "right": "0",
    "bottom": "0",
    "backgroundColor": "rgba(15,23,42,0.5)",
    "zIndex": "1000",
    "alignItems": "center",
    "justifyContent": "center",
}
MODAL_VISIBLE_STYLE: dict[str, str] = {**MODAL_HIDDEN_STYLE, "display": "flex"}


def _range_row(label: str, lo: float, hi: float) -> html.Div:
    return html.Div(
        [
            html.Span(label, style={"color": "#334155", "fontSize": "12px"}),
            html.Span(
                f"{lo:g} - {hi:g}",
                style={
                    "color": "#0f172a",
                    "fontSize": "12px",
                    "fontFamily": "ui-monospace, SFMono-Regular, Menlo, monospace",
                    "fontWeight": "600",
                },
            ),
        ],
        style={
            "display": "flex",
            "justifyContent": "space-between",
            "padding": "4px 0",
            "borderBottom": "1px dashed #e2e8f0",
        },
    )


def build_ranges_modal() -> html.Div:
    """Modal listing direct + derived ranges with a short explanation."""
    direct_rows = [_range_row(key, TRAINING_RANGES[key]["min"], TRAINING_RANGES[key]["max"]) for key in INPUT_TO_RANGE_KEY.values()]
    derived_rows = [_range_row(key, TRAINING_RANGES[key]["min"], TRAINING_RANGES[key]["max"]) for key in DERIVED_RANGE_KEYS if key in TRAINING_RANGES]

    column_title_style = {
        "fontSize": "12px",
        "fontWeight": "700",
        "textTransform": "uppercase",
        "letterSpacing": "0.04em",
        "color": "#64748b",
        "marginBottom": "8px",
    }

    return html.Div(
        id="ranges_modal",
        n_clicks=0,
        children=html.Div(
            [
                html.Div(
                    [
                        html.H3(
                            "Model training envelope",
                            style={"margin": "0", "fontSize": "16px", "color": "#0f172a"},
                        ),
                        html.Button(
                            "x",
                            id="ranges_close_btn",
                            n_clicks=0,
                            style={
                                "border": "none",
                                "background": "transparent",
                                "fontSize": "22px",
                                "lineHeight": "1",
                                "cursor": "pointer",
                                "color": "#64748b",
                                "padding": "0 4px",
                            },
                        ),
                    ],
                    style={
                        "display": "flex",
                        "justifyContent": "space-between",
                        "alignItems": "center",
                        "marginBottom": "10px",
                    },
                ),
                html.P(
                    "Predictions are most reliable when inputs lie within the ranges the model "
                    "was trained on. Values outside these bounds are extrapolated - the model "
                    "still returns a number, but confidence drops.",
                    style={
                        "fontSize": "12px",
                        "color": "#475569",
                        "marginBottom": "14px",
                        "lineHeight": "1.45",
                    },
                ),
                html.Div(
                    [
                        html.Div(
                            [html.Div("Direct inputs", style=column_title_style), *direct_rows],
                            style={"flex": "1", "minWidth": "0"},
                        ),
                        html.Div(
                            [html.Div("Derived features", style=column_title_style), *derived_rows],
                            style={"flex": "1", "minWidth": "0"},
                        ),
                    ],
                    style={"display": "flex", "gap": "24px"},
                ),
                html.Div(
                    "Derived features are computed from geometry inputs - they aren't entered directly, but the same training-range caveat applies.",
                    style={
                        "fontSize": "11px",
                        "color": "#94a3b8",
                        "marginTop": "14px",
                        "fontStyle": "italic",
                    },
                ),
            ],
            style={
                "backgroundColor": "#fff",
                "padding": "20px 22px",
                "borderRadius": "10px",
                "boxShadow": "0 20px 50px rgba(15,23,42,0.25)",
                "maxWidth": "640px",
                "width": "calc(100% - 32px)",
                "maxHeight": "80vh",
                "overflowY": "auto",
            },
        ),
        style=MODAL_HIDDEN_STYLE,
    )
