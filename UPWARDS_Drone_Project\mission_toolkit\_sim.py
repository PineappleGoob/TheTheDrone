"""The laptop simulator. No drone, no camera. It runs your whole mission and prints
a step-by-step trace so you can debug the logic before you ever fly.

The pretend room contains the markers listed in settings.SIM_WORLD_MARKERS.
Delete one there to test what your mission does when a marker is missing.
"""
import time

import settings as S
from . import _brain as brain


class SimBackend:
    def __init__(self, name="mission"):
        self.name = name
        self.world = list(S.SIM_WORLD_MARKERS)
        self._battery = 92
        self._flying = False
        self._navigated = False  # did this sim run fly to a marker? (unlocks a real flight)
        self._locked = None

    # -- helpers -------------------------------------------------------------
    def _p(self, msg):
        print(msg)

    def _tick(self, n=1):
        time.sleep(S.SIM_STEP_SECONDS * n)

    def _drain(self, amount=1):
        self._battery = max(0, self._battery - amount)

    def _require_flying(self, what):
        if not self._flying:
            raise RuntimeError(f"Take off first: call drone.takeoff() before {what}.")

    def _simulate_approach(self):
        """A tiny 1D model of flying in on a marker, so KP/KI/KD actually change what you
        see in sim. The marker starts looking 200 px too small (far away). Each step the
        controller picks a speed; the drone has a little momentum, so gains that are too
        high overshoot and wobble, too low crawl."""
        use_pid = brain.use_pid()
        pid = brain.make_pid(S.KP_SIZE, S.KI_SIZE, S.KD_SIZE, S.MAX_FORWARD_SPEED) if use_pid else None
        err = 200.0     # pixels the marker is away from target size
        vel = 0.0       # the drone's momentum
        dt = S.CONTROL_PERIOD
        lag, gain = 0.2, 18.0
        prev_sign, crossings, overshoot = None, 0, 0.0
        for step in range(1, 121):
            cmd = pid.update(err, dt) if use_pid else brain.steer_speed(err, S.KP_SIZE, S.MAX_FORWARD_SPEED)
            vel += (cmd - vel) * lag
            err -= vel * dt * gain
            if err < 0:
                overshoot = max(overshoot, -err)
            sign = 1 if err >= 0 else -1
            if prev_sign is not None and sign != prev_sign:
                crossings += 1
            prev_sign = sign
            if abs(err) <= S.SIZE_TOLERANCE_PX and abs(vel) < 1.0:
                return step, crossings, overshoot, True
        return 120, crossings, overshoot, False

    def approach_trace(self, use_pid=None):
        """Return (times, errors) for the 1D approach model, for analyze.py --sim.
        Same model the sim verdict uses; here we keep the whole error trace so the
        controls lab can measure it. If use_pid is None, read the current setting."""
        if use_pid is None:
            use_pid = brain.use_pid()
        pid = brain.make_pid(S.KP_SIZE, S.KI_SIZE, S.KD_SIZE, S.MAX_FORWARD_SPEED) if use_pid else None
        err = 200.0
        vel = 0.0
        dt = S.CONTROL_PERIOD
        lag, gain = 0.2, 18.0
        times, errors = [0.0], [err]
        for step in range(1, 121):
            cmd = pid.update(err, dt) if use_pid else brain.steer_speed(err, S.KP_SIZE, S.MAX_FORWARD_SPEED)
            vel += (cmd - vel) * lag
            err -= vel * dt * gain
            times.append(step * dt)
            errors.append(err)
            if abs(err) <= S.SIZE_TOLERANCE_PX and abs(vel) < 1.0:
                break
        return times, errors

    # -- lifecycle -----------------------------------------------------------
    def connect(self):
        self._p(f"[SIM] Pretend drone ready. Battery {self._battery}%. Markers in the room: {self.world}")

    def takeoff(self):
        self._flying = True
        self._drain(2)
        self._p("[SIM] Takeoff. Hovering at about 1 m.")
        self._tick()
        return True

    def land(self):
        self._flying = False
        self._p("[SIM] Landing. Motors off.")
        self._tick()
        return True

    # -- vision / navigation -------------------------------------------------
    def search_for(self, marker_id):
        self._require_flying("search_for")
        self._navigated = True
        self._p(f"[SIM] Searching for marker {marker_id} (turning to look)...")
        self._tick(2)
        self._drain()
        if marker_id in self.world:
            self._locked = marker_id
            self._p(f"[SIM]   Found marker {marker_id}.")
            return True
        self._p(f"[SIM]   Gave up: marker {marker_id} is not in the room.")
        return False

    def search_for_any(self, ids):
        self._require_flying("search_for_any")
        self._navigated = True
        ids = list(ids)
        self._p(f"[SIM] Searching for any of {ids}...")
        self._tick(2)
        self._drain()
        for marker_id in ids:
            if marker_id in self.world:
                self._locked = marker_id
                self._p(f"[SIM]   Found marker {marker_id} first.")
                return marker_id
        self._p(f"[SIM]   None of {ids} are in the room.")
        return None

    def fly_to(self, marker_id):
        self._require_flying("fly_to")
        self._navigated = True
        if marker_id not in self.world:
            self._p(f"[SIM] Cannot fly to marker {marker_id}: it is not in the room.")
            return False
        self._p(f"[SIM] Flying to marker {marker_id}: centering and closing in...")
        self._tick(2)
        self._drain(2)
        steps, crossings, overshoot, ok = self._simulate_approach()
        if (crossings >= 2 and overshoot > 35) or overshoot > 45:
            self._p(f"[SIM]   Wobbly: locked on in {steps} steps but overshot {overshoot:.0f} px. "
                    f"Lower the gain or add some KD to settle it.")
        elif not ok or steps >= 55:
            self._p(f"[SIM]   Slow: took {steps} steps to settle. KP_SIZE may be too low.")
        else:
            self._p(f"[SIM]   Smooth: locked on marker {marker_id} in {steps} steps.")
        self._locked = marker_id
        return True

    # -- signals -------------------------------------------------------------
    def photograph(self, label="photo"):
        self._p(f"[SIM] Photo saved: {label}.jpg")
        self._tick()
        return True

    def celebrate(self):
        self._require_flying("celebrate")
        self._p("[SIM] Celebrate: a little wiggle!")
        self._tick()
        return True

    def flip(self, direction="f"):
        self._require_flying("flip")
        self._p(f"[SIM] Flip {direction}! (needs open space and a full battery on a real drone)")
        self._tick()
        return True

    def dance(self, moves=None):
        self._require_flying("dance")
        self._p(f"[SIM] Dance routine: {moves if moves else 'the default'}")
        self._tick()
        return True

    def say(self, text):
        self._p(f"[SIM] Drone says: {text}")
        return True

    def see(self):
        return self._locked

    # -- info ----------------------------------------------------------------
    @property
    def battery(self):
        return self._battery

    @property
    def height(self):
        return 100 if self._flying else 0

    def fly_manual(self):
        self._p("[SIM] Manual piloting only works on a real drone. Run with sim=False.")
        return False

    def close(self):
        if self._flying:
            self.land()
        self._p(f"[SIM] Mission '{self.name}' complete. Battery {self._battery}%.")
        if self._navigated:
            # Record that a real sim mission ran here (flew to a marker), unlocking a real flight.
            try:
                from pathlib import Path
                Path("flightlogs").mkdir(exist_ok=True)
                (Path("flightlogs") / ".sim_ok").write_text("sim ran ok\n")
            except Exception:
                pass
        return True
