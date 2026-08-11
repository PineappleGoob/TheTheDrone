"""calibrate.py - find the right TARGET_SIDE_PX for your room. No takeoff.

The drone judges distance by how big the marker looks. This tells you that number.

  1. Hang a marker where you want the drone to end up.
  2. Set the drone (powered on) on a box at the exact spot and height you want it to
     hover, pointing at the marker.
  3. Run this. Read the "side" number in pixels.
  4. Put that number into settings.py as TARGET_SIDE_PX.

Press q or ESC to quit. The drone never takes off.

    python calibrate.py
"""
import cv2
from djitellopy import Tello

import settings as S
from mission_toolkit._vision import make_detector, detect_any, draw_observation


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
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # djitellopy gives RGB
            frame = cv2.resize(frame, (S.FRAME_WIDTH, S.FRAME_HEIGHT))
            obs = detect_any(frame, detector)
            if obs is not None:
                print(f"marker {obs.marker_id}:  side = {obs.side_px:6.0f} px   "
                      f"(put this in settings.TARGET_SIDE_PX)", end="\r")
            cv2.imshow("Calibrate - hold at the hover distance - q/ESC to quit",
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
