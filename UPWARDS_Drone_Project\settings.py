"""settings.py — the knobs you are allowed to tune.

Change values here. You should not need to edit anything inside the mission_toolkit folder.
Most of Part 1 and Part 2 is about finding good numbers in this file.
"""

# ---------------------------------------------------------------------------
# Your worlds
# ---------------------------------------------------------------------------
BASE_MARKER = 42            # the "home base" marker your drone lands on at the end

# ---------------------------------------------------------------------------
# LOCK ON control gains
# ---------------------------------------------------------------------------
# Your steer_speed() (and your PID class, if you build it) uses these gains per direction:
#   KP_X    left/right   (keep the marker centered across the frame)
#   KP_Y    up/down      (keep it centered top to bottom)
#   KP_SIZE forward/back (fly in until the marker looks the target size)
# Bigger KP pushes harder. Too big wobbles, too small is slow. Tune these.
# KI and KD do nothing with plain steer_speed (P). They come alive only in the Part 2 PID
# stretch: build the PID class in pid_exercise.py and set USE_PID = True there (not here).
KP_X, KI_X, KD_X = 0.04, 0.0, 0.0          # left/right
KP_Y, KI_Y, KD_Y = 0.04, 0.0, 0.0          # up/down
KP_SIZE, KI_SIZE, KD_SIZE = 0.10, 0.0, 0.0  # forward/back (distance)

# Top speeds (Tello RC units, roughly -100..100). Keep these gentle indoors.
MAX_HORIZONTAL_SPEED = 50
MAX_VERTICAL_SPEED = 50
MAX_FORWARD_SPEED = 50
SEARCH_YAW_SPEED = 15      # how fast it turns while looking for a marker

# How close is "locked on"
CENTER_TOLERANCE_PX = 20    # allowed off-center distance (pixels)
SIZE_TOLERANCE_PX = 18      # allowed error in marker size (pixels)
SETTLE_SECONDS = 1.5        # must stay aligned this long before it counts

# How big a marker should look when the drone has "arrived". Calibrate per room.
TARGET_SIDE_PX = 100

# ---------------------------------------------------------------------------
# Safety and timing
# ---------------------------------------------------------------------------
MIN_BATTERY_PERCENT = 30    # hard floor: the code refuses to fly below this.
                            # Recommended: start every flight above 70 (see DRONE_HANDBOOK).
MAX_SEARCH_SECONDS = 60     # give up looking for a marker after this
MAX_APPROACH_SECONDS = 40  # give up flying to a found marker after this
STALE_SECONDS = 5.0         # if the video freezes this long in flight, land automatically
CONTROL_PERIOD = 0.10       # seconds between control updates
FRAME_WIDTH, FRAME_HEIGHT = 720, 480

# Flips are dramatic but risky. Off by default; a facilitator can set this True.
ALLOW_FLIPS = True

# ---------------------------------------------------------------------------
# Flight rules (you must earn a real flight)
# ---------------------------------------------------------------------------
# Run the simulator at least once before ANY real flight, even manual. It proves your
# setup and code work first. A facilitator can set this False to skip it.
REQUIRE_SIM_FIRST = False
# Finish your five functions (make python check.py pass) before an AUTONOMOUS real flight.
# Manual flight (fly_manual) does not need this. A facilitator can set this False.
REQUIRE_OWN_CODE = False

# ---------------------------------------------------------------------------
# Simulator world  (only used when you run with Drone(sim=True))
# ---------------------------------------------------------------------------
# Which markers "exist" in the pretend room. Delete one to test what your
# mission does when a marker is missing.
SIM_WORLD_MARKERS = [10, 20, 30, 40, 42]
SIM_STEP_SECONDS = 0.4      # how fast the printed simulation plays
