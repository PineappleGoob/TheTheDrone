"""controls_lab.py: measure how good your controller is (advanced, optional).

You have flown on P (steer_speed) and, if you did the stretch, on PID. This is how
engineers decide which is better: with numbers, not opinions. As the drone flies in, the
error (how far the marker is from the target size) starts big and should head to zero.
Three numbers describe that response:

  OVERSHOOT   did it shoot past the target and have to come back? how far, as a percent?
  SETTLING    how long until the error stays small and stops moving?
  STEADY      how much error is left at the very end?

You write the first two below. The third is given. Test them with no drone:

    python check_controls.py

Then see the numbers for real:
    python analyze.py --sim                        compare P vs PID with no drone
    python analyze.py flightlogs/<folder>/telemetry.csv          one real flight
    python analyze.py P_flight.csv PID_flight.csv  two real flights side by side
"""


def overshoot_percent(errors):
    """How far the error swung PAST zero, as a percent of where it started.

    errors: a list of error values over the approach. errors[0] is the biggest; a good
    controller drives it to zero. If the drone overshoots, the error crosses zero and
    spends time on the other side. Return that worst crossing as a percent of the first
    error. Return 0.0 if it never crosses.

    TODO:
      if errors is empty, return 0.0
      start = errors[0]; if start == 0, return 0.0
      biggest_past = 0.0
      for each value in errors:
          how far is it on the OTHER side of zero from start?
             if start > 0:  past = -value      (a negative value is an overshoot)
             else:          past =  value
          if past > biggest_past: biggest_past = past
      return 100.0 * biggest_past / abs(start)
    """
    raise NotImplementedError


def settling_time(times, errors, band_fraction=0.1):
    """The time (seconds) after which the error stays small and stops moving.

    times and errors are two lists of the same length: the seconds, and the error then.
    "Small" means within band_fraction of the first error (default 10 percent).

    TODO:
      if errors is empty, return 0.0
      band = band_fraction * abs(errors[0])
      last_out = None
      for i in range(len(errors)):
          if abs(errors[i]) > band:  last_out = i     # remember the LAST time it was big
      if last_out is None:                 return 0.0                  # never left the band
      if last_out == len(errors) - 1:      return times[-1] - times[0] # never settled
      return times[last_out + 1] - times[0]           # settled on the next reading
    """
    raise NotImplementedError


def steady_state_error(errors, n=5):
    """Given for you: the average size of the last n errors (what is left at the end)."""
    if not errors:
        return 0.0
    tail = errors[-n:]
    return sum(abs(e) for e in tail) / len(tail)
