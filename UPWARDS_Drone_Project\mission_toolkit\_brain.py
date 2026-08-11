"""The bridge between your code and the drone.

The drone asks these functions what to do. Each one calls YOUR version in
student_code.py. Until you write it (or if it errors), the drone quietly uses a backup
version from _reference.py, so it always keeps flying safely. Write your versions, run
`python check.py`, and watch the drone start using your code.
"""
import math

from . import _reference as ref

try:
    import student_code as _student
except Exception:
    _student = None

try:
    import pid_exercise as _pidmod   # the Part 2 PID stretch (optional, may not exist)
except Exception:
    _pidmod = None

_warned = set()


def use_pid():
    """True only if the student turned on the Part 2 PID stretch in pid_exercise.py."""
    return bool(getattr(_pidmod, "USE_PID", False)) if _pidmod else False


_CORE_CHECKS = [
    ("clamp", (0.0, 0.0, 1.0)),
    ("centering_error", (0.0, 0.0)),
    ("steer_speed", (0.0, 0.1, 10.0)),
    ("is_aligned", (0.0, 0.0, 0.0, 10.0, 10.0)),
    ("decide_action", (42,)),
]


def student_core_ready():
    """True only if all five student functions in student_code.py are written (none raise
    NotImplementedError). Used to gate autonomous real flights. A function that is written
    but buggy still counts as ready; check.py is the real correctness gate."""
    if _student is None:
        return False
    for name, args in _CORE_CHECKS:
        fn = getattr(_student, name, None)
        if fn is None:
            return False
        try:
            fn(*args)
        except NotImplementedError:
            return False
        except Exception:
            pass
    return True


def _is_number(x):
    return (isinstance(x, (int, float)) and not isinstance(x, bool)
            and math.isfinite(x))   # reject NaN and infinity so bad math falls back safely


def _call(name, ref_fn, args, want_number=True):
    fn = getattr(_student, name, None) if _student else None
    if fn is None:
        return ref_fn(*args)
    try:
        result = fn(*args)
    except NotImplementedError:
        return ref_fn(*args)
    except Exception as exc:
        if name not in _warned:
            print(f"[brain] your {name}() hit an error, using the backup for now: {exc}")
            _warned.add(name)
        return ref_fn(*args)
    if want_number and not _is_number(result):
        if name not in _warned:
            print(f"[brain] your {name}() did not return a number, using the backup for now.")
            _warned.add(name)
        return ref_fn(*args)
    return result


def clamp(value, low, high):
    return _call('clamp', ref.clamp, (value, low, high))


def centering_error(marker_x, frame_center):
    return _call('centering_error', ref.centering_error, (marker_x, frame_center))


def steer_speed(error, gain, max_speed):
    return _call('steer_speed', ref.steer_speed, (error, gain, max_speed))


def is_aligned(err_x, err_y, err_size, tol_center, tol_size):
    return _call('is_aligned', ref.is_aligned,
                 (err_x, err_y, err_size, tol_center, tol_size), want_number=False)


def decide_action(marker_id):
    return _call('decide_action', ref.decide_action, (marker_id,), want_number=False)


class _SafePID:
    """Wraps the student's PID with the backup PID. Uses the student's output when it is a
    valid number, otherwise falls back. Both advance every step so the backup stays valid."""

    def __init__(self, kp, ki, kd, max_speed):
        self._ref = ref.PID(kp, ki, kd, max_speed)
        self._student = None
        cls = getattr(_pidmod, "PID", None) if _pidmod else None
        if cls is not None:
            try:
                self._student = cls(kp, ki, kd, max_speed)
            except Exception:
                self._student = None

    def update(self, error, dt):
        backup = self._ref.update(error, dt)
        if self._student is None:
            return backup
        try:
            out = self._student.update(error, dt)
        except NotImplementedError:
            return backup
        except Exception as exc:
            if "PID" not in _warned:
                print(f"[brain] your PID.update() hit an error, using the backup for now: {exc}")
                _warned.add("PID")
            return backup
        if not _is_number(out):
            if "PID" not in _warned:
                print("[brain] your PID.update() did not return a number, using the backup for now.")
                _warned.add("PID")
            return backup
        return out


def make_pid(kp, ki, kd, max_speed):
    return _SafePID(kp, ki, kd, max_speed)
