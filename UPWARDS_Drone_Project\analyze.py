"""analyze.py: measure your controller, using your controls_lab.py functions.

    python analyze.py --sim                        compare P vs PID with no drone
    python analyze.py flightlogs/<folder>/telemetry.csv           one real flight
    python analyze.py P_flight.csv PID_flight.csv  two real flights side by side

It prints overshoot, settling time, and leftover error, and saves analyze_figure.png
(the error over time) for your poster. Finish controls_lab.py first, then run
`python check_controls.py`.
"""
import csv
import sys
from pathlib import Path

import controls_lab as lab

MAROON = "#861F41"
ORANGE = "#C64600"


def metrics(label, times, errors):
    try:
        over = lab.overshoot_percent(errors)
        settle = lab.settling_time(times, errors)
    except NotImplementedError:
        print("Finish controls_lab.py first, then run:  python check_controls.py")
        raise SystemExit
    steady = lab.steady_state_error(errors)
    return {"label": label, "over": over, "settle": settle, "steady": steady}


def show_table(results):
    print(f"\n{'controller':<18}{'overshoot':>11}{'settling':>11}{'leftover err':>14}")
    print("-" * 54)
    for r in results:
        print(f"{r['label']:<18}{r['over']:>10.0f}%{r['settle']:>10.2f}s{r['steady']:>13.1f}")
    print()


def save_plot(traces):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    colors = [MAROON, ORANGE, "#2a7", "#26c"]
    plt.figure(figsize=(7, 4))
    for i, (label, t, e) in enumerate(traces):
        plt.plot(t, e, label=label, color=colors[i % len(colors)], linewidth=2)
    plt.axhline(0, color="#999", linewidth=1)
    plt.xlabel("Time (s)")
    plt.ylabel("Error (marker size, px)")
    plt.title("How the error settles")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("analyze_figure.png", dpi=150)
    print("Saved analyze_figure.png")


def trace_from_csv(path):
    """Pull the approach error over time (err_size where a marker was seen)."""
    times, errors = [], []
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            try:
                t = float(row["t_s"])
                e = float(row["err_size"])
            except (KeyError, ValueError, TypeError):
                continue
            times.append(t)
            errors.append(e)
    if times:                       # start the clock at the first reading
        t0 = times[0]
        times = [t - t0 for t in times]
    return times, errors


def run_sim():
    from mission_toolkit._sim import SimBackend
    sim = SimBackend("analyze")
    traces, results = [], []
    for label, use_pid in [("P (steer_speed)", False), ("PID", True)]:
        t, e = sim.approach_trace(use_pid=use_pid)
        traces.append((label, t, e))
        results.append(metrics(label, t, e))
    show_table(results)
    save_plot(traces)


def run_files(paths):
    traces, results = [], []
    for path in paths:
        if not Path(path).exists():
            print(f"File not found: {path}")
            continue
        t, e = trace_from_csv(path)
        if not t:
            print(f"No approach data in {path} (was a marker ever seen on this flight?).")
            continue
        label = Path(path).parent.name or Path(path).name
        traces.append((label, t, e))
        results.append(metrics(label, t, e))
    if results:
        show_table(results)
        save_plot(traces)


def main(argv):
    if not argv:
        print(__doc__)
        return
    if argv[0] == "--sim":
        run_sim()
    else:
        run_files(argv)


if __name__ == "__main__":
    main(sys.argv[1:])
