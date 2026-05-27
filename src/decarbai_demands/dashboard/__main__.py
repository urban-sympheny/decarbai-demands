"""Entry point so `python -m decarbai_demands.dashboard` still works."""

from decarbai_demands.dashboard.app import run_dashboard


if __name__ == "__main__":
    run_dashboard()
