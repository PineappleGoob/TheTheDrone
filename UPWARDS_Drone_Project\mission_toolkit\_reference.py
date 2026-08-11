"""Backup versions of the functions students write in student_code.py.

The drone uses a student's version when it is written and correct, and falls back to
these until then, so the drone always flies. Students should not need to read this file.
"""


def clamp(value, low, high):
    return max(low, min(high, value))


def centering_error(marker_x, frame_center):
    return marker_x - frame_center


def steer_speed(error, gain, max_speed):
    return clamp(gain * error, -max_speed, max_speed)


def is_aligned(err_x, err_y, err_size, tol_center, tol_size):
    return (abs(err_x) <= tol_center
            and abs(err_y) <= tol_center
            and abs(err_size) <= tol_size)


def decide_action(marker_id):
    if marker_id in (10, 20):
        return "photograph"
    if marker_id == 42:
        return "celebrate"
    return "nothing"


class PID:
    """Backup PID controller (used until a student's PID is written and USE_PID is on)."""

    def __init__(self, kp, ki, kd, max_speed):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.max_speed = max_speed
        self.error_total = 0.0
        self.last_error = None

    def update(self, error, dt):
        p = self.kp * error
        self.error_total += error * dt
        if self.ki:  # anti-windup: keep the I term inside the speed limit
            cap = self.max_speed / self.ki
            self.error_total = max(-cap, min(cap, self.error_total))
        i = self.ki * self.error_total
        d = 0.0 if self.last_error is None else self.kd * (error - self.last_error) / dt
        self.last_error = error
        return clamp(p + i + d, -self.max_speed, self.max_speed)


# --- Backups for the advanced / optional tracks (controls_lab.py, distance_lab.py) ------
# Kept here so every function a student can write has a reference version in one place.

def overshoot_percent(errors):
    """Backup for controls_lab.overshoot_percent."""
    if not errors:
        return 0.0
    start = errors[0]
    if start == 0:
        return 0.0
    biggest_past = 0.0
    for value in errors:
        past = -value if start > 0 else value
        if past > biggest_past:
            biggest_past = past
    return 100.0 * biggest_past / abs(start)


def settling_time(times, errors, band_fraction=0.1):
    """Backup for controls_lab.settling_time."""
    if not errors:
        return 0.0
    band = band_fraction * abs(errors[0])
    last_out = None
    for i in range(len(errors)):
        if abs(errors[i]) > band:
            last_out = i
    if last_out is None:
        return 0.0
    if last_out == len(errors) - 1:
        return times[-1] - times[0]
    return times[last_out + 1] - times[0]


def steady_state_error(errors, n=5):
    """Backup for controls_lab.steady_state_error."""
    if not errors:
        return 0.0
    tail = errors[-n:]
    return sum(abs(e) for e in tail) / len(tail)


def distance_meters(side_px, focal_px, marker_size_m):
    """Backup for distance_lab.distance_meters. Pinhole model: farther looks smaller."""
    if side_px <= 0:
        return None
    return focal_px * marker_size_m / side_px
