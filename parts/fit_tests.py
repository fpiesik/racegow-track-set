"""Thin viewer wrapper for the fit-test array."""

from racegow.config import CONFIG
from racegow.connectors import fit_array

model = fit_array(CONFIG)

if __name__ == "__main__":
    try:
        from ocp_vscode import show
    except ImportError as exc:
        raise SystemExit("Install viewer extras: python -m pip install -e .[viewer]") from exc
    show(model, names=["fit_tests"])
