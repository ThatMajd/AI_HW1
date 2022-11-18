import search
import random
import math
import itertools


# When returning state it needs to be hashable

# TODO
# - Use string as a hashable object, i.e. turn the dict into a literal string and then use the library ast
#   which is def more optimized than your code


ids = ["111111111", "111111111"]

PASSABLE = 'P'
IMPASSABLE = 'I'
GAS_STATION = 'G'


def dict_to_tuples(state):
    res = []
    # matrix
    if type(state) == list and state and type(state[0]) == list:
        r = []
        for l in state:
            r.append(tuple(l))
        return tuple(r)
    # reached the base case i.e. literal

    if type(state) != dict:
        if type(state) == list:
            return tuple(state)
        return state

    for key in sorted(list(state.keys())):
        res.append((key, dict_to_tuples(state[key])))
    return tuple(res)


def tuple_to_dict(state):
    a = {}
    p = {}
    taxis = {}

    a[state[0][0]] = state[0][1]
    a[state[1][0]] = p
    pasgs = state[1][1]
    for t in pasgs:
        p[t[0]] = {t[1][0][0]: t[1][0][1],
                   t[1][1][0]: t[1][1][1],
                   t[1][2][0]: t[1][2][1]}
    a[state[2][0]] = taxis # {taxis : {}}
    for t in state[2][1]:

        taxis[t[0]] = {t[1][0][0]: t[1][0][1],
                       t[1][1][0]: t[1][1][1],
                       t[1][2][0]: t[1][2][1],
                       t[1][3][0]: t[1][3][1],
                       t[1][4][0]: list(t[1][4][1])}
    return a


def man_dist(x, y):
    return sum(abs(i-j) for i, j in zip(x, y))


def update_location(state, loc, passengers):
    """
    function takes the state, new location to be updated, and a list of the passengers
    that will be updated.
    we assume that the passengers are on the taxi going to the loc.
    i.e assuming everything is legal
    """
    for passenger in passengers:
        state["passengers"][passenger]["location"] = loc


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

    if matrix[move_to[0]][move_to[1]] == IMPASSABLE:
        return False

    for t in state["taxis"]:
        # Checking that there are no other taxis in the tile to be moved to
        if t != taxi:
            if state["taxis"][t]["location"] == move_to:
                return False
    return True


def can_pickup(state, action):
    taxi = action[1]
    passenger = action[2]
    passenger_location = state["passengers"][passenger]["location"]
    taxi_location = state["taxis"][taxi]["location"]
    capacity = state["taxis"][taxi]["capacity"]

    # Taxi is in the same place as the passenger
    if taxi_location != passenger_location:
        return False

    # There is space in the taxi
    if len(state["taxis"][taxi]["on_board"]) >= capacity:
        return False

    # Passenger has not been picked up
    # there will be a taxi where every passenger is thus this condition is redundant

    # Deleting this condition worsens runtime for some reason
    if state["passengers"][passenger]["picked up"]:
        return False
    return True


def can_dropoff(state, action):
    taxi = action[1]
    passenger = action[2]
    passenger_dist = state["passengers"][passenger]["destination"]
    taxi_location = state["taxis"][taxi]["location"]

    if passenger not in state["taxis"][taxi]["on_board"]:
        return False

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
    # TODO check later whether it's needed
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
    matrix = 0

    def __init__(self, initial):
        """Don't forget to implement the goal test
        You should change the initial to your own representation.
        search.Problem.__init__(self, initial) creates the root node"""

        # Added the parameters to the problem

        for taxi in initial["taxis"]:
            initial["taxis"][taxi]['on_board'] = []
            initial["taxis"][taxi]["max_fuel"] = initial["taxis"][taxi]["fuel"]
        for passenger in initial["passengers"]:
            initial["passengers"][passenger]["picked up"] = False

        self.matrix = initial["map"]
        #del initial["map"]
        self.state = dict_to_tuples(initial)
        search.Problem.__init__(self, self.state)

    def actions(self, state):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        if state != dict:
            state = tuple_to_dict(state)
        taxis = state["taxis"]
        passengers = state["passengers"]
        acts1 = ["move", "pick up", "drop off"]
        acts2 = ["refuel", "wait"]

        actions = []

        for taxi in taxis:
            for pos in local_area(state, taxi):
                if can_move(state, ("move", taxi, pos)):
                    yield(("move", taxi, pos))

            for passenger in passengers:
                if can_pickup(state, ("pick up", taxi, passenger)):
                    yield(("pick up", taxi, passenger))

                if can_dropoff(state, ("drop off", taxi, passenger)):
                    yield(("drop off", taxi, passenger))

            if can_refuel(state, ("refuel", taxi)):
                yield(("refuel", taxi))
            yield(("wait", taxi))

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        if state != dict:
            state = tuple_to_dict(state)

        act = action[0]
        taxi = action[1]
        if act == "move":
            # update taxis and passengers on the taxi's location
            state["taxis"][taxi]["location"] = action[2]
            state["taxis"][taxi]["fuel"] -= 1
            update_location(state, action[2], state["taxis"][taxi]["on_board"])
        elif act == "pick up":
            passenger = action[2]
            state["taxis"][taxi]["on_board"].append(passenger)
            state["passengers"][passenger]["picked up"] = True
        elif act == "drop off":
            passenger = action[2]
            # TODO check later
            state["passengers"][passenger]["location"] = state["passengers"][passenger]["destination"]
            state["taxis"][taxi]["on_board"].remove(passenger)
            # Keep the picked up attribute True so that other taxis don't pick them up
        elif act == "refuel":
            state["taxis"][taxi]["fuel"] = state["taxis"][taxi]["max_fuel"]

        self.state = dict_to_tuples(state)
        return self.state

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state.
             Returns True if it is, False otherwise."""
        if state != dict:
            state = tuple_to_dict(state)
        for passenger in state["passengers"]:
            if state["passengers"][passenger]["location"] != state["passengers"][passenger]["destination"]:
                return False
        for taxi in state["taxis"]:
            # No passengers in the taxis
            if len(state["taxis"][taxi]["on_board"]) > 0:
                return False
        return True

    def h(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""
        return self.h_1(node) + self.h_2(node)

    def h_1(self, node):
        """
        This is a simple heuristic
        """
        state = tuple_to_dict(node.state)
        unpicked = 0
        picked_not_delivered = 0
        for passenger in state["passengers"]:
            if not state["passengers"][passenger]["picked up"]:
                unpicked += 1
            else:
                if state["passengers"][passenger]["location"] != state["passengers"][passenger]["destination"]:
                    picked_not_delivered += 1
        num_taxis = len(state["taxis"])

        return (2*unpicked + picked_not_delivered) / num_taxis

    def h_2(self, node):
        """
        This is a slightly more sophisticated Manhattan heuristic
        """
        # TODO check correctness
        state = tuple_to_dict(node.state)
        d, t = 0, 0
        for passenger in state["passengers"]:
            if not state["passengers"][passenger]["picked up"]:
                d += man_dist(state["passengers"][passenger]["location"], state["passengers"][passenger]["destination"])
            else:
                t += man_dist(state["passengers"][passenger]["location"], state["passengers"][passenger]["destination"])
        return (d + t) / len(state["taxis"])

    """Feel free to add your own functions
    (-2, -2, None) means there was a timeout"""


def create_taxi_problem(game):
    return TaxiProblem(game)



