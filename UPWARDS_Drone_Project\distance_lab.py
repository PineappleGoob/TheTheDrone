"""distance_lab.py: turn the marker's size in pixels into a real distance (advanced, optional).

A camera becomes a ruler once you know two things: how big the object really is, and your
camera's "focal length" in pixels. The marker's black square is 150 mm (0.15 m) across, so:

        distance = FOCAL_PX * MARKER_SIZE_M / side_px

The farther away the marker, the smaller it looks (fewer pixels), so the distance goes up
as side_px goes down. You write distance_meters(). Test it with no drone:

    python check_distance.py

Then find YOUR camera's FOCAL_PX once (a one-time calibration):
  1. Tape-measure a spot a known distance from the marker, say 1.0 m. Set the powered-on
     drone there, run  python calibrate.py , and read the "side" number in pixels.
  2. Compute FOCAL_PX with the helper below, for example at 1.0 m:
        python -c "import distance_lab as d; print(d.focal_px_from(SIDE_PX_YOU_READ, 1.0))"
  3. Put that number into FOCAL_PX below.

Then  python measure_distance.py  prints the live distance; check it against your tape.
"""

MARKER_SIZE_M = 0.15     # the black square is 150 mm across (see make_markers.py)
FOCAL_PX = 900.0         # a rough starting value; calibrate it for your camera (see above)


def distance_meters(side_px):
    """Return the distance to the marker in metres, from how wide it looks in pixels.

    TODO:
      if side_px is 0 or less, we cannot tell, so return None
      otherwise return  FOCAL_PX * MARKER_SIZE_M / side_px
    """
    raise NotImplementedError


def focal_px_from(side_px, distance_m):
    """Given for you: work out FOCAL_PX from one measurement at a known distance."""
    return side_px * distance_m / MARKER_SIZE_M


def target_side_px_for(distance_m):
    """Given for you: the side px a marker shows at a chosen distance. Use it to set a
    standoff, for example put  settings.TARGET_SIDE_PX = target_side_px_for(1.5)  to make
    the drone stop 1.5 m from the marker."""
    return FOCAL_PX * MARKER_SIZE_M / distance_m
