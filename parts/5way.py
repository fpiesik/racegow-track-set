"""Thin viewer/export wrapper for the 5way connector."""

from racegow.config import CONFIG
from racegow.connectors import connector_by_name

model = connector_by_name("5way", CONFIG)

if __name__ == "__main__":
    try:
        from ocp_vscode import show
    except ImportError as exc:
        raise SystemExit("Install viewer extras: python -m pip install -e .[viewer]") from exc
    show(model, names=["5way"])
