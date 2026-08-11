"""This is where YOU write the drone's brain.

Fill in each function below where it says TODO. The drone really uses these to fly.
Test your work any time, with no drone, by running:

    python check.py

Until you finish a function, the drone uses a backup version, so it still flies. Your
goal is to make all of check.py pass with your own code, and then watch the drone fly
on the logic you wrote.

Only edit this file. You do not need to change anything inside the mission_toolkit folder.
"""


def clamp(value, low, high):
    """Keep a number inside a range.
    If value is below low, return low. If it is above high, return high.
    Otherwise return value unchanged.

    clamp(12, 0, 10)  ->  10
    clamp(-3, 0, 10)  ->  0
    clamp(5, 0, 10)   ->  5
    """
    # TODO: return value, but never below low and never above high.
    #       Hint: Python has min() and max().
    raise NotImplementedError


def centering_error(marker_x, frame_center):
    """How far the marker is from the middle of the picture, left or right, in pixels.
    Positive means the marker is to the right of center, negative means to the left.

    centering_error(400, 360)  ->  40
    centering_error(300, 360)  ->  -60
    """
    # TODO: return the marker's x position minus the center.
    raise NotImplementedError


def steer_speed(error, gain, max_speed):
    """Turn an error into a speed. This is a proportional controller: bigger error,
    bigger push. Multiply the error by the gain, then keep the answer between
    -max_speed and +max_speed so the drone never flies too fast.

    steer_speed(100, 0.1, 20)  ->  10
    steer_speed(500, 0.1, 20)  ->  20    (would be 50, but capped at 20)
    steer_speed(-500, 0.1, 20) ->  -20
    """
    # TODO: return gain * error, clamped to the range [-max_speed, max_speed].
    #       Hint: you already wrote clamp() above. You can call it here.
    raise NotImplementedError


def is_aligned(err_x, err_y, err_size, tol_center, tol_size):
    """True only when the marker is centered AND at the right distance.
    err_x and err_y must each be within tol_center of zero, and err_size within
    tol_size of zero.

    is_aligned(5, -3, 2, 35, 18)   ->  True
    is_aligned(50, 0, 0, 35, 18)   ->  False   (too far left/right)
    is_aligned(0, 0, 40, 35, 18)   ->  False   (wrong distance)
    """
    # TODO: return True when all three errors are small enough.
    #       Hint: use abs() and the word 'and'.
    raise NotImplementedError


def decide_action(marker_id):
    """Decide what the drone should do when it reaches a marker.
    Return exactly one of these words: "photograph", "celebrate", "dance", or "nothing".

    This one is yours to design. Make it fit your mission and your theme.
    Marker ids: 10 SAMPLE A, 20 SAMPLE B, 30 WAYPOINT 1, 40 WAYPOINT 2, 42 HOME BASE.
    """
    # TODO: use if / elif to choose an action, and end with:  else: return "nothing"
    #       so EVERY marker gets a valid answer. check.py tests all five: 10, 20, 30, 40, 42.
    raise NotImplementedError
