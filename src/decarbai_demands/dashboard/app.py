"""Dash app factory and entry point."""

from dash import Dash

from decarbai_demands.dashboard.callbacks import register_callbacks
from decarbai_demands.dashboard.layout import build_layout


_INDEX_TEMPLATE = """<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>* {margin: 0; padding: 0; box-sizing: border-box;}</style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>"""


def create_app() -> Dash:
    """Create and configure the Dash application."""
    app = Dash(__name__)
    app.index_string = _INDEX_TEMPLATE
    app.layout = build_layout()
    register_callbacks(app)
    return app


def run_dashboard(port: int = 8050, debug: bool = False) -> None:
    """Run the dashboard."""
    app = create_app()
    app.run(port=port, debug=debug)


if __name__ == "__main__":
    run_dashboard()
