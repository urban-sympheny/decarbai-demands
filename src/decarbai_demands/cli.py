import sys


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "dashboard":
        from decarbai_demands.dashboard.app import run_dashboard

        run_dashboard()
    else:
        print("Usage: decarbai-demands dashboard")
        sys.exit(1)
