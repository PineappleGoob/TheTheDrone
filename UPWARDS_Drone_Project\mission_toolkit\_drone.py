"""The Drone facade. Same verbs whether you are in the simulator or flying for real.

    drone = Drone(sim=True)    # laptop simulator
    drone = Drone(sim=False)   # real Tello

Every verb returns something useful (True/False, or the marker id it found) so you can
branch and loop in your own mission.
"""
from ._sim import SimBackend


class MissionAbort(Exception):
    """Raised when the pilot presses q or ESC. The drone has already been landed;
    this just stops the rest of the mission from running."""


class Drone:
    def __init__(self, sim=True, log=True, name="mission"):
        self.sim = sim
        self._actions = []   # a record of what the drone did, for your tests in my_tests.py
        if sim:
            self._b = SimBackend(name=name)
        else:
            # Imported only for real flights, so the simulator needs no camera libraries.
            from ._real import RealBackend
            self._b = RealBackend(name=name, log=log)
        self._b.connect()

    def actions(self):
        """A list of what the drone has done, like [('takeoff',), ('fly_to', 10), ('land',)].
        Use this in my_tests.py to check your mission did what you expected."""
        return list(self._actions)

    # -- flight --------------------------------------------------------------
    def takeoff(self):
        """Take off and hover."""
        result = self._b.takeoff()
        self._actions.append(('takeoff',))
        return result

    def land(self):
        """Land straight down where the drone is now."""
        result = self._b.land()
        self._actions.append(('land',))
        return result

    # -- find and go ---------------------------------------------------------
    def search_for(self, marker_id):
        """Turn in place until this marker is seen. Returns True if found."""
        result = self._b.search_for(marker_id)
        self._actions.append(('search_for', marker_id))
        return result

    def search_for_any(self, ids):
        """Turn in place until any of these markers is seen. Returns the id found, or None."""
        result = self._b.search_for_any(ids)
        self._actions.append(('search_for_any', result))
        return result

    def fly_to(self, marker_id):
        """Find the marker, then fly in and center on it. Returns True if it locked on."""
        result = self._b.fly_to(marker_id)
        self._actions.append(('fly_to', marker_id))
        return result

    def land_on(self, marker_id):
        """Fly to a marker, then land there. Returns True if it reached the marker first."""
        reached = self.fly_to(marker_id)
        self.land()
        return reached

    def visit(self, ids):
        """Fly to each marker in order. Returns the list of markers it actually reached."""
        reached = []
        for marker_id in ids:
            if self.fly_to(marker_id):
                reached.append(marker_id)
        return reached

    # -- signals -------------------------------------------------------------
    def photograph(self, label="photo"):
        """Save a photo of what the drone sees right now."""
        result = self._b.photograph(label)
        self._actions.append(('photograph', label))
        return result

    def celebrate(self):
        """A small, safe wiggle to show success."""
        result = self._b.celebrate()
        self._actions.append(('celebrate',))
        return result

    def flip(self, direction="f"):
        """A flip (f, b, l, r). Needs open space and a strong battery. Use with care."""
        result = self._b.flip(direction)
        self._actions.append(('flip', direction))
        return result

    def dance(self, moves=None):
        """Run a short choreography. Pass your own list of moves, or leave blank for the default."""
        result = self._b.dance(moves)
        self._actions.append(('dance',))
        return result

    def say(self, text):
        """Print a line in your drone's voice (great for your demo video)."""
        result = self._b.say(text)
        self._actions.append(('say', text))
        return result

    def see(self):
        """Return the id of a marker in view right now, or None."""
        return self._b.see()

    # -- your decisions ------------------------------------------------------
    def decide(self, marker_id):
        """Ask your decide_action() in student_code.py what to do at this marker.
        Returns one of: "photograph", "celebrate", "dance", "nothing"."""
        from . import _brain
        return _brain.decide_action(marker_id)

    def do(self, action):
        """Run the action word that decide() returned."""
        action = (action or "nothing").lower()
        if action == "photograph":
            return self.photograph("evidence")
        if action == "celebrate":
            return self.celebrate()
        if action == "dance":
            return self.dance()
        return None

    # -- info ----------------------------------------------------------------
    @property
    def battery(self):
        """Battery percent."""
        return self._b.battery

    @property
    def height(self):
        """Height above the floor, in cm."""
        return self._b.height

    def fly_manual(self):
        """Pilot the real drone with the keyboard (Part 1). Simulator will just say so."""
        return self._b.fly_manual()

    # -- cleanup -------------------------------------------------------------
    def done(self):
        """Always call this at the end. Lands if needed and closes everything."""
        return self._b.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.done()
        # A pilot abort or a blocked flight both end here. Swallow it so the script ends quietly.
        if exc_type is not None and issubclass(exc_type, MissionAbort):
            print("Flight stopped. The drone is on the ground.")
            return True
        return False
