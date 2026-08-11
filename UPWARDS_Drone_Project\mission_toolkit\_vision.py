"""Marker detection helpers (used only for real flights). Wraps OpenCV ArUco."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import cv2
import numpy as np


@dataclass(frozen=True)
class MarkerObservation:
    marker_id: int
    center_x: float
    center_y: float
    side_px: float
    corners: np.ndarray


def make_detector():
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters()
    return cv2.aruco.ArucoDetector(dictionary, parameters)


def _observation_from(pts, marker_id) -> MarkerObservation:
    pts = pts.reshape(4, 2).astype(np.float32)
    center = pts.mean(axis=0)
    side_lengths = [np.linalg.norm(pts[(i + 1) % 4] - pts[i]) for i in range(4)]
    return MarkerObservation(
        marker_id=int(marker_id),
        center_x=float(center[0]),
        center_y=float(center[1]),
        side_px=float(np.mean(side_lengths)),
        corners=pts,
    )


def detect_marker(frame, detector, target_id) -> Optional[MarkerObservation]:
    """Return the observation for one specific marker id, or None."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = detector.detectMarkers(gray)
    if ids is None:
        return None
    ids_flat = ids.flatten().tolist()
    if target_id not in ids_flat:
        return None
    index = ids_flat.index(target_id)
    return _observation_from(corners[index], target_id)


def detect_any(frame, detector, wanted=None) -> Optional[MarkerObservation]:
    """Return the first marker seen (optionally restricted to a set of ids), or None."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = detector.detectMarkers(gray)
    if ids is None:
        return None
    for pts, mid in zip(corners, ids.flatten().tolist()):
        if wanted is None or mid in wanted:
            return _observation_from(pts, mid)
    return None


def draw_observation(frame, observation, errors=None):
    output = frame.copy()
    h, w = output.shape[:2]
    cv2.drawMarker(output, (w // 2, h // 2), (255, 255, 255), cv2.MARKER_CROSS, 20, 2)
    if observation is None:
        cv2.putText(output, 'Marker not detected', (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        return output
    pts = observation.corners.astype(int).reshape((-1, 1, 2))
    cv2.polylines(output, [pts], True, (0, 255, 0), 2)
    cv2.circle(output, (int(observation.center_x), int(observation.center_y)), 5, (0, 255, 0), -1)
    cv2.putText(output, f'ID={observation.marker_id} side={observation.side_px:.0f}px',
                (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)
    if errors is not None:
        ex, ey, es = errors
        cv2.putText(output, f'ex={ex:.0f} ey={ey:.0f} es={es:.0f}',
                    (15, 58), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    return output
