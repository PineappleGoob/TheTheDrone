"""Small helpers for your tests in my_tests.py.

Each one takes the list you get from drone.actions() and answers a yes/no question about
what your mission did. Import them like:

    from mission_toolkit import took_off, landed, visited, photos_taken
"""


def took_off(log):
    """True if the drone took off during the mission."""
    return ('takeoff',) in log


def landed(log):
    """True if the drone landed during the mission."""
    return ('land',) in log


def visited(log, marker_id):
    """True if the drone flew to this marker."""
    return ('fly_to', marker_id) in log


def photos_taken(log):
    """A list of the labels of every photo the drone took."""
    return [action[1] for action in log if action and action[0] == 'photograph']
