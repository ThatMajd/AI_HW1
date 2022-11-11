import search
import random
import math
import itertools


ids = ["111111111", "111111111"]

PASSABLE = 'P'
IMPASSABLE = 'I'
GAS_STATION = 'G'


def can_move(state, action):
    # Check fuel level
    # Can pass
    taxi = action[1]
    fuel = state["taxis"][taxi]["fuel"]
    matrix = state["map"]
    taxi_location = state["taxis"][taxi]["location"]
    move_to = action[2]

    if fuel <= 0:
        return False
    if abs(taxi_location[0] - move_to[0]) + abs(taxi_location[1] - move_to[1]) != 1:
        # Move isn't legal
        return False

    if matrix[move_to[0]][move_to[1]] == IMPASSABLE:
        return False

    for t in state["taxis"]:
        # Checking that there are no other taxis in the tile to be moved to
        if t != taxi:
            if state["taxis"][t]["location"] == taxi_location:
                return False
    return True


def can_pickup(state, action):
    taxi = action[1]
    passenger = action[2]
    passenger_location = state["passenger"][passenger]["location"]
    taxi_location = state["taxis"][taxi]["location"]
    capacity = state["taxis"][taxi]["capacity"]

    # Taxi is in the same place as the passenger
    if taxi_location != passenger_location:
        return False

    # There is space in the taxi
    if len(state["taxis"][taxi]["on_board"]) >= capacity:
        return False

    return True


def can_dropoff(state, action):
    taxi = action[1]
    passenger = action[2]
    passenger_dist = state["passenger"][passenger]["destination"]
    taxi_location = state["taxis"][taxi]["location"]

    if passenger_dist != taxi_location:
        return False
    return True


def can_refuel(state, action):
    taxi = action[1]
    taxi_location = state["taxis"][taxi]["location"]
    fuel = state["taxis"][taxi]["fuel"]
    max_fuel = state["taxis"][taxi]["max_fuel"]

    if taxi_location != GAS_STATION:
        return False
    # TODO
    if max_fuel == fuel:
        return False
    return True

def local_area(state, taxi):
    matrix = state["map"]
    rows = len(matrix) - 1
    cols = len(matrix[0]) - 1
    taxi_loc = state["taxis"][taxi]["location"]
    x, y = taxi_loc
    res = []
    if x+1 <= rows and y <= cols:
        res.append((x+1, y))
    if x <= rows and y + 1 <= cols:
        res.append((x, y+1))
    if x-1 >= 0 and y <= cols:
        res.append((x-1, y))
    if x <= rows and y-1 >= 0:
        res.append((x, y-1))
    return res


class TaxiProblem(search.Problem):
    """This class implements a medical problem according to problem description file"""

    def __init__(self, initial):
        """Don't forget to implement the goal test
        You should change the initial to your own representation.
        search.Problem.__init__(self, initial) creates the root node"""

        # Added the parameters to the problem

        for taxi in initial["taxis"]:
            initial["taxis"][taxi]['on_board'] = []
            initial["taxis"][taxi]["max_fuel"] = initial["taxis"][taxi]["fuel"]
        for passenger in
        self.state = initial
        # TODO
        search.Problem.__init__(self, initial)

    def actions(self, state):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        taxis = state["taxis"]
        passengers = state["passengers"]
        acts1 = ["move", "pick up", "drop off"]
        acts2 = ["refuel", "wait"]

        actions = []

        for taxi in taxis:
            wait_flag = True
            for passenger, pos in zip(passengers, local_area(self.state, taxi)):
                # TODO passenger is incorrect we need to give it a point
                if can_move(self.state, ("move", taxi, pos)):
                    actions.append(("move", taxi, pos))
                    wait_flag = False

                if can_pickup(self.state, ("pick up", taxi, passenger)):
                    actions.append(("pick up", taxi, passenger))
                    wait_flag = False

                if can_dropoff(self.state, ("drop off", taxi, passenger)):
                    actions.append(("drop off", taxi, passenger))
                    wait_flag = False

                if can_refuel(self.state, ("refuel", taxi)):
                    actions.append(("refuel", taxi))
                    wait_flag = False
            if wait_flag:
                actions.append(("wait", taxi))

        return actions

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        act = action[0]
        taxi = action[1]
        if act == "move":
            state["taxis"][taxi]["location"] = act[2]
            state["taxis"][taxi]["fuel"] -= 1
        elif act == "pick up":
            passenger = act[2]
            state["taxis"][taxi]["on_board"].append(passenger)

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state.
         Returns True if it is, False otherwise."""

    def h(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""
        return 0

    def h_1(self, node):
        """
        This is a simple heuristic
        """

    def h_2(self, node):
        """
        This is a slightly more sophisticated Manhattan heuristic
        """

    """Feel free to add your own functions
    (-2, -2, None) means there was a timeout"""


def create_taxi_problem(game):
    return TaxiProblem(game)

