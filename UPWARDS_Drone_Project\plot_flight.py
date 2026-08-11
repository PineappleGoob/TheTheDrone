"""plot_flight.py - turn a real flight log into a figure for your poster.

    python plot_flight.py flightlogs/example_20260101_120000/telemetry.csv

It saves flight_figure.png next to the log. Two panels:
  top    - how high the drone flew over time
  bottom - the marker growing bigger as the drone closed in (its approach)
Write a caption that explains what your figure shows.
"""
import csv
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

MAROON = "#861F41"
ORANGE = "#C64600"


def num(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def main(csv_path):
    csv_path = Path(csv_path)
    if not csv_path.exists():
        print(f"File not found: {csv_path}")
        return
    rows = list(csv.DictReader(open(csv_path, newline="")))
    if not rows:
        print("The log is empty.")
        return

    t = [num(r.get("t_s")) for r in rows]
    height = [num(r.get("h")) for r in rows]

    # marker size only where a marker was actually seen (the approach curve)
    seen_t, seen_size = [], []
    for r in rows:
        s = num(r.get("side_px"))
        tt = num(r.get("t_s"))
        if s and tt is not None:
            seen_t.append(tt)
            seen_size.append(s)

    fig, ax = plt.subplots(2, 1, figsize=(7, 6), sharex=True)
    ax[0].plot(t, height, color=MAROON, linewidth=2)
    ax[0].set_ylabel("Height (cm)")
    ax[0].set_title("Our flight")
    ax[0].grid(True, alpha=0.3)

    if seen_t:
        ax[1].plot(seen_t, seen_size, ".", color=ORANGE, markersize=5)
    ax[1].set_ylabel("Marker size (px)")
    ax[1].set_xlabel("Time (s)")
    ax[1].set_title("Closing in on the marker")
    ax[1].grid(True, alpha=0.3)

    fig.tight_layout()
    out = csv_path.parent / "flight_figure.png"
    fig.savefig(out, dpi=150)
    print(f"Saved {out}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python plot_flight.py <path to telemetry.csv>")
        sys.exit(1)
    main(sys.argv[1])
