"""pid_exercise.py: the Part 2 PID stretch (advanced, optional).

Your steer_speed() in student_code.py is a P (proportional) controller. A PID adds two more
parts, I and D, so the drone flies in more smoothly. This is that exercise.

  1) Fill in the update() method of the PID class below.
  2) Test it with no drone:      python check_pid.py
  3) Set USE_PID = True (just below) and run  python example_mission.py  in the simulator.
     At KP_SIZE = 0.40 the "Wobbly" approach becomes "Smooth" once you add some KD_SIZE.
  4) Then fly on your PID in a flight slot.

Leave USE_PID = False until your PID passes check_pid.py.
"""
from student_code import clamp   # reuse the clamp() you already wrote

USE_PID = False


class PID:
    """A controller with memory. steer_speed() was only the P (proportional) part.
      I (integral):  adds up the error over time, to close a gap that never quite goes away.
      D (derivative): reacts to how fast the error is changing, to stop overshoot.
    __init__ sets up the memory for you. You write update().
    """

    def __init__(self, kp, ki, kd, max_speed):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.max_speed = max_speed
        self.error_total = 0.0    # running sum of the error, for the I part
        self.last_error = None    # the previous error, for the D part

    def update(self, error, dt):
        """Return a speed for this error. dt is the seconds since the last update.

        TODO, build the three parts and clamp the sum:
          p = self.kp * error
          add error * dt to self.error_total, then  i = self.ki * self.error_total
          d = 0.0 on the first call (self.last_error is None), otherwise
              self.kd * (error - self.last_error) / dt
          remember for next time:  self.last_error = error
          return clamp(p + i + d, -self.max_speed, self.max_speed)
        """
        raise NotImplementedError
