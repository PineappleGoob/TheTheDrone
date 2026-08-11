"""mission_toolkit — the friendly drone library for the UPWARDS drone project.

    from mission_toolkit import Drone

    drone = Drone(sim=True)   # True = test on your laptop, False = fly a real drone
    drone.takeoff()
    drone.fly_to(10)
    drone.land_on(42)
    drone.done()

Tune behavior in settings.py. You should not need to edit files in here.
"""
from ._drone import Drone, MissionAbort
from .testkit import took_off, landed, visited, photos_taken

__all__ = ["Drone", "MissionAbort", "took_off", "landed", "visited", "photos_taken"]
