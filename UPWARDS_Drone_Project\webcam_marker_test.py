"""webcam_marker_test.py - test marker detection with your laptop camera (no drone).

Hold a printed marker up to the camera. A green box locks on and shows the marker id
and its size in pixels. This is exactly how the drone finds things. The size in pixels
is what the drone uses to judge distance, so watch it grow as you move the marker closer.

Press q or ESC to quit.
"""
import cv2

import settings as S
from mission_toolkit._vision import make_detector, detect_any, draw_observation


def main(camera_index=0):
    detector = make_detector()
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"Could not open webcam index {camera_index}. Try 1 or 2.")
        return
    print("Show a printed marker to the camera. Press q or ESC to quit.")
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frame = cv2.resize(frame, (S.FRAME_WIDTH, S.FRAME_HEIGHT))
            obs = detect_any(frame, detector)
            cv2.imshow("Webcam marker test - q/ESC to quit", draw_observation(frame, obs))
            if (cv2.waitKey(1) & 0xFF) in (ord("q"), 27):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
