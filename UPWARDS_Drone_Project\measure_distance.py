"""measure_distance.py: see the marker's distance in metres, live. No takeoff.

Uses your distance_meters() from distance_lab.py. Hold the powered-on drone at a spot you
measured with a tape, run this, and compare the printed metres to your tape. If they
disagree, calibrate FOCAL_PX in distance_lab.py (that file explains how).

    python measure_distance.py            (q or ESC to quit)
"""
import cv2
from djitellopy import Tello

import settings as S
import distance_lab
from mission_toolkit import _reference as ref
from mission_toolkit._vision import make_detector, detect_any, draw_observation

_warned = [False]


def measure(side_px):
    """Your distance_meters() from distance_lab.py, or the backup if you have not written
    it yet (so this tool always shows a number)."""
    try:
        return distance_lab.distance_meters(side_px)
    except NotImplementedError:
        if not _warned[0]:
            print("[note] distance_meters() is not written yet; using the backup. Write your own "
                  "in distance_lab.py (test it with: python check_distance.py).")
            _warned[0] = True
        return ref.distance_meters(side_px, distance_lab.FOCAL_PX, distance_lab.MARKER_SIZE_M)


def main():
    tello = Tello()
    tello.connect()
    print(f"Battery {tello.get_battery()}%. Streaming, no takeoff. Press q or ESC to quit.")
    tello.streamon()
    reader = tello.get_frame_read()
    detector = make_detector()
    try:
        while True:
            frame = reader.frame
            if frame is None:
                continue
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)   # djitellopy gives RGB
            frame = cv2.resize(frame, (S.FRAME_WIDTH, S.FRAME_HEIGHT))
            obs = detect_any(frame, detector)
            if obs is not None:
                metres = measure(obs.side_px)
                if metres is not None:
                    print(f"marker {obs.marker_id}:  side = {obs.side_px:5.0f} px   "
                          f"distance = {metres:4.2f} m     ", end="\r")
            cv2.imshow("Measure distance - hold at a known spot - q/ESC to quit",
                       draw_observation(frame, obs))
            if (cv2.waitKey(1) & 0xFF) in (ord("q"), 27):
                break
    finally:
        try:
            tello.streamoff()
        except Exception:
            pass
        tello.end()
        cv2.destroyAllWindows()
        print()


if __name__ == "__main__":
    main()
