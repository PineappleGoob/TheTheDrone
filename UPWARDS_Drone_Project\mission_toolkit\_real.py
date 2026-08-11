"""The real-drone backend. Wraps a Tello, the vision, a proportional control loop, and logging.

Heavy libraries (OpenCV, djitellopy) are imported here, not in the simulator, so a
student with no drone can still run everything in sim mode.

Every real flight writes flightlogs/<name>_<timestamp>/:
  telemetry.csv   one row per control step (drone state + vision + commands)
  flight.mp4      the drone's camera view (FPV) for the whole flight, takeoff to landing
plus any photos the mission saved.

The video is captured by a background recorder thread so it covers the ENTIRE flight,
not just the moments the control loop is running. It records the annotated view while
the drone is chasing a marker, and the raw camera view the rest of the time.
"""
import csv
import re
import threading
import time
from datetime import datetime
from pathlib import Path

import settings as S
from . import _brain as brain
from ._drone import MissionAbort

STATE_KEYS = [
    'bat', 'h', 'tof', 'baro', 'time',
    'pitch', 'roll', 'yaw',
    'vgx', 'vgy', 'vgz',
    'agx', 'agy', 'agz',
    'templ', 'temph',
]
BASE_FIELDS = ['t_s', 'phase', 'event', 'frame_idx']
VISION_FIELDS = ['marker_seen', 'marker_id', 'cx', 'cy', 'side_px', 'err_x', 'err_y', 'err_size']
CMD_FIELDS = ['cmd_lr', 'cmd_fb', 'cmd_ud', 'cmd_yaw']


class _H264Writer:
    """Records BGR frames to an H.264 mp4 with PyAV, so the file plays in ordinary video
    players (Windows Movies & TV, Mac QuickTime, browsers, PowerPoint). OpenCV's mp4v
    writes MPEG-4 Part 2 instead, which those players often refuse to open."""

    def __init__(self, av, path, fps, size):
        self._av = av
        self._container = av.open(str(path), mode="w")
        self._stream = self._container.add_stream("libx264", rate=int(fps))
        self._stream.width, self._stream.height = size
        self._stream.pix_fmt = "yuv420p"
        self._closed = False

    def isOpened(self):
        return not self._closed

    def write(self, frame_bgr):
        frame = self._av.VideoFrame.from_ndarray(frame_bgr, format="bgr24")
        for packet in self._stream.encode(frame):
            self._container.mux(packet)

    def release(self):
        if self._closed:
            return
        self._closed = True
        try:
            for packet in self._stream.encode():   # flush libx264's buffered frames
                self._container.mux(packet)
        except Exception:
            pass
        try:
            self._container.close()
        except Exception:
            pass


class RealBackend:
    def __init__(self, name="mission", log=True):
        self.name = name
        self.log_enabled = log
        self._flying = False
        self._locked = None
        self._session = None
        self._logf = None
        self._writer = None
        self._video = None
        self._video_path = None
        self._fps = max(1, round(1.0 / S.CONTROL_PERIOD))
        self._rec_thread = None
        self._rec_stop = None
        self._last_display = None      # most recent annotated frame, for the recorder thread
        self._last_display_t = 0.0
        self._t0 = None
        self._frame_idx = 0
        self._gate_blocked = False     # set True if the "run sim first" rule stopped the flight

    # -- lifecycle -----------------------------------------------------------
    def connect(self):
        # Flight rule 1: you must run the simulator first (even for manual flight).
        from pathlib import Path
        if getattr(S, "REQUIRE_SIM_FIRST", True) and not (Path("flightlogs") / ".sim_ok").exists():
            print("[DRONE] Run the simulator first, e.g.  python example_mission.py  (or your")
            print("        my_mission.py). It proves your code and setup before you fly.")
            print("        (A facilitator can set REQUIRE_SIM_FIRST = False in settings.py.)")
            self._gate_blocked = True
            return

        import cv2
        from djitellopy import Tello
        from . import _vision

        self._cv2 = cv2
        self._vision = _vision

        self._tello = Tello()
        self._tello.connect()
        battery = self._tello.get_battery()
        print(f"[DRONE] Connected. Battery {battery}%.")
        if battery < S.MIN_BATTERY_PERCENT:
            raise RuntimeError(f"Battery {battery}% is below {S.MIN_BATTERY_PERCENT}%. Charge before flying.")

        self._tello.streamon()
        self._reader = self._tello.get_frame_read()
        self._detector = _vision.make_detector()
        self._t0 = time.monotonic()
        if self.log_enabled:
            self._open_log()
        time.sleep(2.0)  # let the video stream settle
        self._start_recorder()  # begin recording the FPV now, so the whole flight is captured

    def _open_log(self):
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._session = Path("flightlogs") / f"{self.name}_{stamp}"
        self._session.mkdir(parents=True, exist_ok=True)
        self._logf = open(self._session / "telemetry.csv", "w", newline="")
        self._writer = csv.DictWriter(
            self._logf, fieldnames=BASE_FIELDS + VISION_FIELDS + CMD_FIELDS + STATE_KEYS)
        self._writer.writeheader()
        self._video, self._video_path = self._open_video()
        print(f"[DRONE] Logging to {self._session}")

    def _open_video(self):
        """Open a video writer, matching the loop rate so playback speed is right.

        Preferred path is H.264 via PyAV: the file plays in normal video players on Windows
        and Mac. OpenCV's mp4v writes MPEG-4 Part 2, which many players refuse, so it is only
        a last-resort fallback (MJPG AVI, which at least plays in most desktop players)."""
        size = (S.FRAME_WIDTH, S.FRAME_HEIGHT)
        try:
            import av
            path = self._session / "flight.mp4"
            return _H264Writer(av, path, self._fps, size), path
        except Exception as exc:
            print(f"[DRONE] H.264 recorder unavailable ({exc}); using a fallback format.")
        for tag, ext in (("MJPG", "avi"), ("mp4v", "mp4")):
            path = self._session / f"flight.{ext}"
            try:
                writer = self._cv2.VideoWriter(
                    str(path), self._cv2.VideoWriter_fourcc(*tag), self._fps, size)
            except Exception:
                continue
            if writer.isOpened():
                print(f"[DRONE] Recording as {path.name} ({tag}).")
                return writer, path
            writer.release()
        print("[DRONE] Video recording off: no working video writer on this laptop.")
        return None, None

    def _start_recorder(self):
        """Background thread: write the current view to the video at a steady rate, for the
        whole flight, whatever the control loop is doing."""
        if not self._video:
            return
        self._rec_stop = threading.Event()
        self._rec_thread = threading.Thread(target=self._record_loop, name="fpv-recorder", daemon=True)
        self._rec_thread.start()

    def _record_loop(self):
        period = 1.0 / self._fps
        w, h = S.FRAME_WIDTH, S.FRAME_HEIGHT
        while not self._rec_stop.is_set():
            t0 = time.monotonic()
            display, age = self._last_display, t0 - self._last_display_t
            frame = display if (display is not None and age < 0.4) else self._grab()
            if frame is not None and self._video is not None:
                try:
                    if frame.shape[1] != w or frame.shape[0] != h:
                        frame = self._cv2.resize(frame, (w, h))
                    self._video.write(frame)
                except Exception:
                    pass
            self._rec_stop.wait(max(0.0, period - (time.monotonic() - t0)))

    def _log(self, phase, event="", obs=None, errors=None, commands=None):
        if not self._writer:
            return
        row = {name: '' for name in self._writer.fieldnames}
        row['t_s'] = round(time.monotonic() - self._t0, 3)
        row['phase'] = phase
        row['event'] = event
        row['frame_idx'] = self._frame_idx
        row['marker_seen'] = 1 if obs is not None else 0
        if obs is not None:
            row['marker_id'] = obs.marker_id
            row['cx'] = round(obs.center_x, 1)
            row['cy'] = round(obs.center_y, 1)
            row['side_px'] = round(obs.side_px, 1)
        if errors is not None:
            row['err_x'], row['err_y'], row['err_size'] = (round(e, 1) for e in errors)
        if commands is not None:
            row['cmd_lr'], row['cmd_fb'], row['cmd_ud'], row['cmd_yaw'] = commands
        try:
            state = self._tello.get_current_state() or {}
        except Exception:
            state = {}
        for key in STATE_KEYS:
            row[key] = state.get(key, '')
        self._writer.writerow(row)
        self._logf.flush()

    # -- flight --------------------------------------------------------------
    def takeoff(self):
        if self._gate_blocked:
            raise MissionAbort()
        # Flight rule 2: finish your own code before an autonomous flight (takeoff is only
        # called by autonomous missions; manual flight uses fly_manual and is exempt).
        if getattr(S, "REQUIRE_OWN_CODE", True) and not brain.student_core_ready():
            print("[DRONE] Finish your code first: make  python check.py  pass (5 of 5), then fly.")
            print("        (A facilitator can set REQUIRE_OWN_CODE = False in settings.py.)")
            raise MissionAbort()
        battery = self.battery
        try:
            answer = input(f"Battery {battery}%. Cage closed, glasses on, props clear? Type FLY to take off: ").strip()
        except EOFError:
            answer = ""  # no console (e.g. an IDE run button): do not take off
        if answer != "FLY":
            print("Takeoff cancelled.")
            raise MissionAbort()
        self._log('takeoff', 'takeoff_cmd')
        self._tello.takeoff()
        self._flying = True
        self._log('takeoff', 'airborne')
        time.sleep(2.0)
        return True

    def land(self):
        self._log('land', 'land_cmd')
        try:
            self._tello.send_rc_control(0, 0, 0, 0)
            self._tello.land()
        except Exception as exc:
            print(f"[DRONE] Land command failed: {exc}")
        finally:
            self._flying = False
        self._log('land', 'landed')
        return True

    # -- the LOCK ON control loop -------------------------------------------
    def _clamp(self, value, limit):
        return int(max(-limit, min(limit, round(value))))

    def _check_keys(self, phase):
        """Read one keypress each loop.
        q or ESC: land and stop the mission.
        e: facilitator EMERGENCY stop (cuts the motors; the drone drops, which is only
           safe inside the cage)."""
        key = self._cv2.waitKey(1) & 0xFF
        if key == ord('e'):
            self._log(phase, 'emergency_stop')
            print("[DRONE] EMERGENCY STOP. Motors cut.")
            try:
                self._tello.emergency()
            except Exception:
                pass
            self._flying = False
            raise MissionAbort()
        if key in (ord('q'), 27):
            self._abort(phase)

    def _abort(self, phase):
        """Pilot pressed q/ESC (or the video froze). Land now and stop the whole mission."""
        self._log(phase, 'operator_abort')
        print("[DRONE] Abort. Landing.")
        self.land()
        raise MissionAbort()

    def _grab(self):
        frame = self._reader.frame
        if frame is None:  # djitellopy rarely returns None, but stay safe
            return None
        # djitellopy 2.5 gives RGB frames; OpenCV expects BGR for imwrite/VideoWriter.
        frame = self._cv2.cvtColor(frame, self._cv2.COLOR_RGB2BGR)
        return self._cv2.resize(frame, (S.FRAME_WIDTH, S.FRAME_HEIGHT))

    def fly_to(self, marker_id, target_side=None, phase="approach"):
        """Search for the marker, then fly in using your control code (student_code.py)
        until centered and at target size."""
        target_side = S.TARGET_SIDE_PX if target_side is None else target_side

        search_start = time.monotonic()
        approach_start = None
        stable_since = None
        last_sig = None
        last_change_t = search_start

        # Part 2 stretch: fly on the student's PID if they turned it on, else steer_speed (P).
        use_pid = brain.use_pid()
        last_ctrl_t = None
        if use_pid:
            pid_x = brain.make_pid(S.KP_X, S.KI_X, S.KD_X, S.MAX_HORIZONTAL_SPEED)
            pid_y = brain.make_pid(S.KP_Y, S.KI_Y, S.KD_Y, S.MAX_VERTICAL_SPEED)
            pid_s = brain.make_pid(S.KP_SIZE, S.KI_SIZE, S.KD_SIZE, S.MAX_FORWARD_SPEED)

        while True:
            frame = self._grab()
            if frame is None:
                self._check_keys(phase)   # keep q/ESC and the e-stop working during a frame stall
                time.sleep(S.CONTROL_PERIOD)
                continue
            self._frame_idx += 1
            now = time.monotonic()

            # Frozen-video failsafe: if the picture stops changing, the feed froze; land.
            sig = int(frame[::32, ::32].sum())
            if sig != last_sig:
                last_sig, last_change_t = sig, now
            elif now - last_change_t > S.STALE_SECONDS:
                print("[DRONE] Video froze. Landing for safety.")
                self._abort(phase)

            obs = self._vision.detect_marker(frame, self._detector, marker_id)

            if obs is None:
                if approach_start is None:
                    if now - search_start > S.MAX_SEARCH_SECONDS:
                        self._tello.send_rc_control(0, 0, 0, 0)
                        self._log(phase, 'search_timeout')
                        print(f"[DRONE] Could not find marker {marker_id}.")
                        return False
                else:
                    if now - approach_start > S.MAX_APPROACH_SECONDS:
                        self._tello.send_rc_control(0, 0, 0, 0)
                        self._log(phase, 'approach_timeout')
                        print(f"[DRONE] Lost marker {marker_id} during approach.")
                        return False
                commands = (0, 0, 0, S.SEARCH_YAW_SPEED)
                self._tello.send_rc_control(*commands)
                stable_since = None
                display = self._vision.draw_observation(frame, None)
                self._log(phase, 'searching', obs=None, commands=commands)
            else:
                first_sight = approach_start is None
                if first_sight:
                    approach_start = now
                elif now - approach_start > S.MAX_APPROACH_SECONDS:
                    self._tello.send_rc_control(0, 0, 0, 0)
                    self._log(phase, 'approach_timeout', obs=obs)
                    return False

                # These lines use YOUR code from student_code.py (with a safe backup).
                err_x = brain.centering_error(obs.center_x, S.FRAME_WIDTH / 2.0)
                err_y = brain.centering_error(obs.center_y, S.FRAME_HEIGHT / 2.0)
                err_size = target_side - obs.side_px
                if use_pid:
                    dt = S.CONTROL_PERIOD if last_ctrl_t is None else max(1e-3, now - last_ctrl_t)
                    last_ctrl_t = now
                    left_right = self._clamp(pid_x.update(err_x, dt), S.MAX_HORIZONTAL_SPEED)
                    up_down = self._clamp(-pid_y.update(err_y, dt), S.MAX_VERTICAL_SPEED)
                    forward_back = self._clamp(pid_s.update(err_size, dt), S.MAX_FORWARD_SPEED)
                else:
                    left_right = self._clamp(brain.steer_speed(err_x, S.KP_X, S.MAX_HORIZONTAL_SPEED), S.MAX_HORIZONTAL_SPEED)
                    up_down = self._clamp(-brain.steer_speed(err_y, S.KP_Y, S.MAX_VERTICAL_SPEED), S.MAX_VERTICAL_SPEED)
                    forward_back = self._clamp(brain.steer_speed(err_size, S.KP_SIZE, S.MAX_FORWARD_SPEED), S.MAX_FORWARD_SPEED)
                commands = (left_right, forward_back, up_down, 0)
                self._tello.send_rc_control(*commands)

                errors = (err_x, err_y, err_size)
                aligned = brain.is_aligned(err_x, err_y, err_size, S.CENTER_TOLERANCE_PX, S.SIZE_TOLERANCE_PX)
                display = self._vision.draw_observation(frame, obs, errors)
                self._log(phase, 'acquired' if first_sight else 'aligning',
                          obs=obs, errors=errors, commands=commands)
                if aligned:
                    if stable_since is None:
                        stable_since = now
                    elif now - stable_since >= S.SETTLE_SECONDS:
                        self._tello.send_rc_control(0, 0, 0, 0)
                        self._locked = marker_id
                        self._log(phase, 'aligned', obs=obs, errors=errors, commands=(0, 0, 0, 0))
                        print(f"[DRONE] Locked on marker {marker_id}.")
                        self._show(display)
                        return True
                else:
                    stable_since = None

            self._show(display, phase, search_start, approach_start)
            self._check_keys(phase)
            time.sleep(S.CONTROL_PERIOD)

    def _show(self, display, phase="", search_start=None, approach_start=None):
        cv2 = self._cv2
        if search_start is not None:
            if approach_start is None:
                mode, remaining = 'SEARCH', S.MAX_SEARCH_SECONDS - (time.monotonic() - search_start)
            else:
                mode, remaining = 'APPROACH', S.MAX_APPROACH_SECONDS - (time.monotonic() - approach_start)
            try:
                state = self._tello.get_current_state() or {}
            except Exception:
                state = {}
            cv2.putText(display,
                        f'{phase} {mode} {max(0.0, remaining):4.1f}s | bat={state.get("bat","?")}% '
                        f'| q/ESC: land',
                        (12, S.FRAME_HEIGHT - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
        # Hand the annotated frame to the recorder thread (it does the writing).
        self._last_display = display
        self._last_display_t = time.monotonic()
        cv2.imshow('Drone mission - q/ESC to land', display)

    # -- find helpers (no flying) -------------------------------------------
    def search_for(self, marker_id):
        """Turn in place until the marker is seen, then stop. Does not fly toward it."""
        start = time.monotonic()
        last_sig, last_change_t = None, start
        while time.monotonic() - start < S.MAX_SEARCH_SECONDS:
            frame = self._grab()
            if frame is None:
                self._check_keys('search')   # keep q/ESC and the e-stop working during a frame stall
                time.sleep(S.CONTROL_PERIOD)
                continue
            self._frame_idx += 1
            sig = int(frame[::32, ::32].sum())
            if sig != last_sig:
                last_sig, last_change_t = sig, time.monotonic()
            elif time.monotonic() - last_change_t > S.STALE_SECONDS:
                print("[DRONE] Video froze. Landing for safety.")
                self._abort('search')
            obs = self._vision.detect_marker(frame, self._detector, marker_id)
            if obs is not None:
                self._tello.send_rc_control(0, 0, 0, 0)
                self._locked = marker_id
                self._log('search', 'found', obs=obs)
                self._show(self._vision.draw_observation(frame, obs))
                return True
            self._tello.send_rc_control(0, 0, 0, S.SEARCH_YAW_SPEED)
            self._log('search', 'searching')
            self._show(self._vision.draw_observation(frame, None), 'search', start, None)
            self._check_keys('search')
            time.sleep(S.CONTROL_PERIOD)
        self._tello.send_rc_control(0, 0, 0, 0)
        self._log('search', 'search_timeout')
        return False

    def search_for_any(self, ids):
        wanted = set(ids)
        start = time.monotonic()
        last_sig, last_change_t = None, start
        while time.monotonic() - start < S.MAX_SEARCH_SECONDS:
            frame = self._grab()
            if frame is None:
                self._check_keys('search')   # keep q/ESC and the e-stop working during a frame stall
                time.sleep(S.CONTROL_PERIOD)
                continue
            self._frame_idx += 1
            sig = int(frame[::32, ::32].sum())
            if sig != last_sig:
                last_sig, last_change_t = sig, time.monotonic()
            elif time.monotonic() - last_change_t > S.STALE_SECONDS:
                print("[DRONE] Video froze. Landing for safety.")
                self._abort('search')
            obs = self._vision.detect_any(frame, self._detector, wanted)
            if obs is not None:
                self._tello.send_rc_control(0, 0, 0, 0)
                self._locked = obs.marker_id
                self._log('search', 'found', obs=obs)
                self._show(self._vision.draw_observation(frame, obs))
                return obs.marker_id
            self._tello.send_rc_control(0, 0, 0, S.SEARCH_YAW_SPEED)
            self._log('search', 'searching')
            self._show(self._vision.draw_observation(frame, None), 'search', start, None)
            self._check_keys('search')
            time.sleep(S.CONTROL_PERIOD)
        self._tello.send_rc_control(0, 0, 0, 0)
        self._log('search', 'search_timeout')
        return None

    # -- signals -------------------------------------------------------------
    def photograph(self, label="photo"):
        frame = self._grab()
        if frame is None:
            return False
        obs = self._vision.detect_any(frame, self._detector)
        annotated = self._vision.draw_observation(frame, obs)
        folder = self._session if self._session else Path('.')
        stamp = datetime.now().strftime('%H%M%S')
        safe_label = re.sub(r'[^A-Za-z0-9_-]', '_', label) or 'photo'
        path = folder / f"photo_{safe_label}_{stamp}.jpg"
        self._cv2.imwrite(str(path), annotated)
        print(f"[DRONE] Photo saved: {path}")
        self._log('signal', f'photo:{label}', obs=obs)
        return True

    def celebrate(self):
        """A gentle safe wiggle (a small yaw left then right). No flip."""
        if not self._flying:
            return False
        self._log('signal', 'celebrate')
        for yaw in (30, -30, 30, -30):
            self._tello.send_rc_control(0, 0, 0, yaw)
            time.sleep(0.25)
        self._tello.send_rc_control(0, 0, 0, 0)
        return True

    def flip(self, direction="f"):
        """A real flip. Off by default; a facilitator sets ALLOW_FLIPS in settings.
        Needs open space and battery above 50 percent."""
        if not self._flying:
            return False
        if not getattr(S, "ALLOW_FLIPS", False):
            print("[DRONE] Flips are turned off. Ask a facilitator to set ALLOW_FLIPS = True.")
            return False
        try:
            if self._tello.get_battery() < 50:
                print("[DRONE] Skipping flip: battery too low.")
                return False
            self._log('signal', f'flip:{direction}')
            self._tello.flip(direction)
            return True
        except Exception as exc:
            print(f"[DRONE] Flip failed: {exc}")
            return False

    def dance(self, moves=None):
        moves = moves or ['celebrate']
        for move in moves:
            if move == 'celebrate':
                self.celebrate()
            elif move in ('f', 'b', 'l', 'r'):
                self.flip(move)
            time.sleep(0.2)
        return True

    def say(self, text):
        print(f"[DRONE] {text}")
        self._log('signal', f'say:{text[:40]}')
        return True

    def see(self):
        frame = self._grab()
        if frame is None:
            return None
        obs = self._vision.detect_any(frame, self._detector)
        return obs.marker_id if obs else None

    # -- info ----------------------------------------------------------------
    @property
    def battery(self):
        try:
            return self._tello.get_battery()
        except Exception:
            return 0

    @property
    def height(self):
        try:
            return self._tello.get_height()
        except Exception:
            return 0

    # -- Part 1 manual piloting ----------------------------------------------
    def fly_manual(self):
        """Keyboard piloting. w/s forward-back, a/d left-right, r/f up-down, z/x yaw,
        t takeoff, l land, q or ESC to quit. Keep the window focused.

        A held key repeats slowly, so we keep the last command for a moment (LATCH_S)
        after each keypress. Without this the drone stutters instead of flying smoothly."""
        if self._gate_blocked:   # "run sim first" also applies to manual flight
            raise MissionAbort()
        cv2 = self._cv2
        speed = 40
        LATCH_S = 0.5   # hold the last command this long after a keypress (Windows key-repeat is ~0.5 s)
        last_cmd = (0, 0, 0, 0)
        last_key_t = 0.0
        print("[DRONE] Manual mode. Keys: w/s a/d r/f z/x, t=takeoff l=land q/ESC=quit.")
        while True:
            frame = self._grab()
            if frame is not None:
                cv2.putText(frame, 'MANUAL  w/s a/d r/f z/x  t=takeoff l=land q/ESC=quit',
                            (12, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                cv2.imshow('Manual flight', frame)
            key = cv2.waitKey(1) & 0xFF
            moved = True
            if key == ord('w'): last_cmd = (0, speed, 0, 0)
            elif key == ord('s'): last_cmd = (0, -speed, 0, 0)
            elif key == ord('a'): last_cmd = (-speed, 0, 0, 0)
            elif key == ord('d'): last_cmd = (speed, 0, 0, 0)
            elif key == ord('r'): last_cmd = (0, 0, speed, 0)
            elif key == ord('f'): last_cmd = (0, 0, -speed, 0)
            elif key == ord('z'): last_cmd = (0, 0, 0, -speed)
            elif key == ord('x'): last_cmd = (0, 0, 0, speed)
            elif key == ord('t'):
                if self.battery < S.MIN_BATTERY_PERCENT:
                    print(f"[DRONE] Battery too low to take off ({self.battery}%).")
                    continue
                self._tello.takeoff(); self._flying = True; continue
            elif key == ord('l'):
                self._tello.land(); self._flying = False; continue
            elif key in (ord('q'), 27):
                break
            else:
                moved = False
            if moved:
                last_key_t = time.monotonic()
            cmd = last_cmd if (time.monotonic() - last_key_t) < LATCH_S else (0, 0, 0, 0)
            if self._flying:
                self._tello.send_rc_control(*cmd)
            time.sleep(0.02)
        if self._flying:
            self._tello.land(); self._flying = False
        return True

    # -- cleanup -------------------------------------------------------------
    def close(self):
        try:
            if self._flying:
                self._tello.send_rc_control(0, 0, 0, 0)
                self._tello.land()
                self._flying = False
        except Exception as exc:
            print(f"[DRONE] Cleanup landing failed: {exc}")
        # stop the recorder thread before releasing the writer so no frame is written after release
        if self._rec_stop is not None:
            self._rec_stop.set()
        if self._rec_thread is not None:
            self._rec_thread.join(timeout=2.0)
        if self._video is not None:
            try:
                self._video.release()
            except Exception:
                pass
        try:
            self._tello.streamoff()
        except Exception:
            pass
        try:
            self._tello.end()
        except Exception:
            pass
        try:
            self._cv2.destroyAllWindows()
        except Exception:
            pass
        if self._logf:
            self._logf.close()
            print(f"[DRONE] Log saved: {self._session / 'telemetry.csv'}")
        if self._video_path is not None:
            print(f"[DRONE] Video saved: {self._video_path}")
        return True
