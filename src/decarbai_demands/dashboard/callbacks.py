"""Dash callbacks: prediction, CSV download, live range validation, modal toggle."""

import io
import json

import plotly.graph_objects as go
from dash import Dash, Input, Output, State, ctx
from pydantic import ValidationError

from decarbai_demands.dashboard.ranges import (
    INPUT_TO_RANGE_KEY,
    MODAL_HIDDEN_STYLE,
    MODAL_VISIBLE_STYLE,
    TRAINING_RANGES,
)
from decarbai_demands.dashboard.styles import AMBER, HELPER_STYLE, INPUT_STYLE
from decarbai_demands.pipeline import run_pipeline
from decarbai_demands.schema import InputData


_DEMAND_COLORS = {"heating": "#e74c3c", "cooling": "#3498db", "electricity": "#f39c12", "dhw": "#9b59b6"}
_DOWNLOAD_BUTTON_HIDDEN = {"display": "none"}
_DOWNLOAD_BUTTON_VISIBLE = {
    "padding": "8px 16px",
    "backgroundColor": "#10b981",
    "color": "white",
    "border": "none",
    "borderRadius": "6px",
    "fontSize": "13px",
    "cursor": "pointer",
    "fontWeight": "600",
}


def _empty_figure(*, with_axes: bool = True) -> go.Figure:
    fig = go.Figure()
    if with_axes:
        fig.update_layout(xaxis_title="Hour of Year", yaxis_title="Demand [kWh]", template="plotly_white")
    else:
        fig.update_layout(template="plotly_white")
    return fig


def _build_profile_figure(profiles: dict[str, list[float]], city: str, building_type: str) -> go.Figure:
    fig = go.Figure()
    hours = list(range(8760))
    for dt, values in profiles.items():
        fig.add_trace(
            go.Scatter(
                x=hours,
                y=values,
                mode="lines",
                name=dt.title(),
                line={"color": _DEMAND_COLORS.get(dt, "#333"), "width": 1},
                hovertemplate=f"{dt.title()}<br>Hour: %{{x}}<br>Demand: %{{y:.2f}} kWh<extra></extra>",
            )
        )
    fig.update_layout(
        title=f"Energy Demand Profiles - {city.replace('_', ' ').title()} ({building_type.upper()})",
        xaxis_title="Hour of Year",
        yaxis_title="Demand [kWh]",
        template="plotly_white",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
        hovermode="x unified",
    )
    return fig


def _register_prediction_callback(app: Dash) -> None:
    @app.callback(
        [Output("profile_plot", "figure"), Output("status_message", "children"), Output("download_button", "style")],
        Input("run_button", "n_clicks"),
        [
            State("city", "value"),
            State("building_type", "value"),
            State("demand_types", "value"),
            State("length", "value"),
            State("width", "value"),
            State("floor_height", "value"),
            State("number_of_floors", "value"),
            State("construction_year", "value"),
            State("north_angle", "value"),
            State("nwwr", "value"),
            State("ewwr", "value"),
            State("swwr", "value"),
            State("wwwr", "value"),
            State("u_ground", "value"),
            State("u_wall", "value"),
            State("u_roof", "value"),
            State("u_window", "value"),
        ],
        prevent_initial_call=False,
    )
    def run_prediction(
        n_clicks: int,
        city: str,
        building_type: str,
        demand_types: list[str],
        length: float,
        width: float,
        floor_height: float,
        number_of_floors: int,
        construction_year: int,
        north_angle: float,
        nwwr: float,
        ewwr: float,
        swwr: float,
        wwwr: float,
        u_ground: float,
        u_wall: float,
        u_roof: float,
        u_window: float,
    ) -> tuple[go.Figure, str, dict[str, str]]:
        if not demand_types:
            return _empty_figure(), "⚠️ Please select at least one demand type", _DOWNLOAD_BUTTON_HIDDEN

        if n_clicks == 0:
            return _empty_figure(), "Configure parameters and click 'Run Prediction'", _DOWNLOAD_BUTTON_HIDDEN

        try:
            input_data = InputData(
                country="ch",
                city=city,
                building_type=building_type,
                demand_type=demand_types,
                length=length,
                width=width,
                floor_height=floor_height,
                number_of_floors=number_of_floors,
                construction_year=construction_year,
                north_angle=north_angle,
                nwwr=nwwr,
                ewwr=ewwr,
                swwr=swwr,
                wwwr=wwwr,
                u_ground=u_ground,
                u_wall=u_wall,
                u_roof=u_roof,
                u_window=u_window,
            )
            profiles = run_pipeline(input_data)
            fig = _build_profile_figure(profiles, city, building_type)
            totals = {k: f"{sum(v):.0f} kWh" for k, v in profiles.items()}
            status = "✅ Annual totals: " + " | ".join([f"{k.title()}: {v}" for k, v in totals.items()])
            return fig, status, _DOWNLOAD_BUTTON_VISIBLE
        except ValidationError as e:
            errors = " | ".join([f"{'.'.join(map(str, err['loc']))}: {err['msg']}" for err in e.errors()])
            return _empty_figure(with_axes=False), "❌ " + errors, _DOWNLOAD_BUTTON_HIDDEN
        except Exception as e:
            return _empty_figure(with_axes=False), f"❌ Error: {e!s}", _DOWNLOAD_BUTTON_HIDDEN


def _register_download_callback(app: Dash) -> None:
    @app.callback(
        Output("download_csv", "data"),
        Input("download_button", "n_clicks"),
        State("profile_plot", "figure"),
        State("city", "value"),
        State("building_type", "value"),
        prevent_initial_call=True,
    )
    def download_csv(n_clicks: int, figure: dict, city: str, building_type: str) -> dict[str, str] | None:
        if not figure or "data" not in figure or not figure["data"]:
            return None
        columns = {trace.get("name", "Unknown").lower(): trace.get("y", []) for trace in figure["data"] if trace.get("y")}
        if not columns:
            return None
        output = io.StringIO()
        headers = list(columns.keys())
        output.write(",".join(headers) + "\n")
        for i in range(len(next(iter(columns.values())))):
            output.write(",".join(str(columns[h][i]) for h in headers) + "\n")
        return {"content": output.getvalue(), "filename": f"demand_profiles_{city}_{building_type}.csv"}


def _register_range_validation_callbacks(app: Dash) -> None:
    """Clientside callbacks: amber border + amber helper text when value escapes the trained envelope."""
    input_style_normal = json.dumps(INPUT_STYLE)
    input_style_amber = json.dumps({**INPUT_STYLE, "border": f"1px solid {AMBER}"})
    helper_style_normal = json.dumps(HELPER_STYLE)
    helper_style_amber = json.dumps({**HELPER_STYLE, "color": AMBER, "fontWeight": "600"})

    for input_id, range_key in INPUT_TO_RANGE_KEY.items():
        lo = TRAINING_RANGES[range_key]["min"]
        hi = TRAINING_RANGES[range_key]["max"]
        app.clientside_callback(
            f"""
            function(v) {{
                const lo = {lo}, hi = {hi};
                const baseText = 'Trained: ' + lo + ' - ' + hi;
                const empty = (v === null || v === undefined || v === '');
                const out = !empty && (v < lo || v > hi);
                if (out) {{
                    return [{input_style_amber}, {helper_style_amber}, '⚠ ' + baseText];
                }}
                return [{input_style_normal}, {helper_style_normal}, baseText];
            }}
            """,
            [
                Output(input_id, "style"),
                Output(f"{input_id}_helper", "style"),
                Output(f"{input_id}_helper", "children"),
            ],
            Input(input_id, "value"),
        )


def _register_modal_callback(app: Dash) -> None:
    @app.callback(
        Output("ranges_modal", "style"),
        Input("ranges_info_btn", "n_clicks"),
        Input("ranges_close_btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def toggle_ranges_modal(_open: int, _close: int) -> dict[str, str]:
        return MODAL_VISIBLE_STYLE if ctx.triggered_id == "ranges_info_btn" else MODAL_HIDDEN_STYLE


def register_callbacks(app: Dash) -> None:
    """Wire every callback onto the Dash app."""
    _register_prediction_callback(app)
    _register_download_callback(app)
    _register_range_validation_callbacks(app)
    _register_modal_callback(app)
