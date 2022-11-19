from copy import deepcopy

import search
import random
import math
import itertools


# When returning state it needs to be hashable

# TODO
# - Use string as a hashable object, i.e. turn the dict into a literal string and then use the library ast
#   which is def more optimized than your code
# BUSTED doesn't affect

# - Check if the problem is solvable


ids = ["111111111", "111111111"]

PASSABLE = 'P'
IMPASSABLE = 'I'
GAS_STATION = 'G'


def dict_to_tuples(state):
    res = []
    # reached the base case i.e. literal
    if type(state) != dict:
        if type(state) == list:
            return tuple(state)
        return state

    for key in sorted(list(state.keys())):
        res.append((key, dict_to_tuples(state[key])))
    return tuple(res)


def tuple_to_dict(state):
    res = {}
    passengers = state[0][1]
    taxis = state[1]
    res[state[0][0]] = {}
    for passenger in passengers:
        res[state[0][0]][passenger[0]] = {att[0]: att[1] for att in passenger[1]}

    res[taxis[0]] = {}
    for taxi in taxis[1]:
        res[taxis[0]][taxi[0]] = {att[0]: att[1] for att in taxi[1]}
        res[taxis[0]][taxi[0]]["on_board"] = list(res[taxis[0]][taxi[0]]["on_board"])

    return res


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


def can_move(state, action, matrix):
    # Check fuel level
    # Can pass
    taxi = action[1]
    fuel = state["taxis"][taxi]["fuel"]
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
    # if max_fuel == fuel:
    #     return False
    return True


def local_area(state, taxi, matrix):
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


def solvable(state, matrix):
    imp = set()
    for row, _ in enumerate(matrix):
        for col, _ in enumerate(matrix[0]):
            if matrix[row][col] == IMPASSABLE:
                imp.add((row, col))
    passengers = state["passengers"]
    for passenger in passengers:
        if state["passengers"][passenger]["location"] in imp or state["passengers"][passenger]["destination"] in imp:

            return False

    return True


class TaxiProblem(search.Problem):
    """This class implements a medical problem according to problem description file"""
    matrix = 0
    is_solvable = True

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
        del initial["map"]
        if not solvable(initial, self.matrix):
            self.is_solvable = True
            print("Problem unsolvable")

        self.state = dict_to_tuples(initial)
        search.Problem.__init__(self, self.state)

    def actions(self, state):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        if not self.is_solvable:
            return [(-2, -2, None)]
        state = tuple_to_dict(state)
        taxis = state["taxis"]
        passengers = state["passengers"]

        # TODO a valid action consists of a move for each taxi
        # so if we have 3 taxis the output of this function should be of the form
        # [(move_for_taxi_1), (move_for_taxi_2), (move_for_taxi_2)]
        things = {}
        for taxi in taxis:
            things[taxi] = []
            loc = state["taxis"][taxi]["location"]
            for pos in local_area(state, taxi, self.matrix):
                if can_move(state, ("move", taxi, pos), self.matrix):
                    things[taxi].append((("move", taxi, pos), pos))

            for passenger in passengers:
                if can_pickup(state, ("pick up", taxi, passenger)):
                    things[taxi].append((("pick up", taxi, passenger), loc))

                if can_dropoff(state, ("drop off", taxi, passenger)):
                    things[taxi].append((("drop off", taxi, passenger), loc))

            if can_refuel(state, ("refuel", taxi)):
                things[taxi].append((("refuel", taxi), loc))
            things[taxi].append((("wait", taxi), loc))
        actions = list(itertools.product(*things.values()))

        for action in actions:
            seen = set()
            for taxi_act in action[0]:
                if taxi_act[1] not in seen:
                    seen.add(taxi_act[1])
                else:
                    break
                yield tuple(t[0] for t in action)

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        state = tuple_to_dict(state)
        for c in action:
            act = c[0]
            taxi = c[1]
            if act == "move":
                # update taxis and passengers on the taxi's location
                state["taxis"][taxi]["location"] = c[2]
                state["taxis"][taxi]["fuel"] -= 1
                update_location(state, c[2], state["taxis"][taxi]["on_board"])
            elif act == "pick up":
                passenger = c[2]
                state["taxis"][taxi]["on_board"].append(passenger)
                state["passengers"][passenger]["picked up"] = True
            elif act == "drop off":
                passenger = c[2]
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





#
# import search
# import random
# import math
# from copy import deepcopy
# import ast
# import itertools
#
# ids = ["209028869", "206016446"]
#
#
# class TaxiProblem(search.Problem):
#     """This class implements a medical problem according to problem description file"""
#     map = []
#
#     const_taxis = {}
#     const_passengers = {}
#
#     state = ""
#
#     num_taxis = 0
#     num_passengers = 0
#
#     def __init__(self, initial):
#         """Don't forget to implement the goal test
#         You should change the initial to your own representation.
#         search.Problem.__init__(self, initial) creates the root node"""
#         self.map = initial['map']
#
#         self.const_taxis = initial["taxis"]
#         self.const_passengers = initial["passengers"]
#
#         self_state = deepcopy(initial)
#         self_state.pop("map")
#
#         for taxi in self_state["taxis"].keys():
#             self_state["taxis"][taxi]["capacity"] = 0
#             self_state["taxis"][taxi]["passengers_names"] = []
#
#         for name in self_state["passengers"].keys():
#             self_state["passengers"][name].pop("destination")
#             self_state["passengers"][name]["taxi"] = "none"
#
#         self.state = str(self_state)
#
#         self.num_taxis = len(self.const_taxis.keys())
#         self.num_passengers = len(self.const_passengers.keys())
#
#         search.Problem.__init__(self, self.state)
#
#     def actions(self, state):
#         """Returns all the actions that can be executed in the given
#         state. The result should be a tuple (or other iterable) of actions
#         as defined in the problem description file"""
#         self_state = ast.literal_eval(self.state)
#         state = ast.literal_eval(state)
#         actions_taxi = {}
#         taxis = self_state["taxis"].keys()
#         passengers = self_state["passengers"].keys()
#         for taxi in taxis:
#             taxi_loc = state["taxis"][taxi]["location"]
#             current_actions = []
#             if state["taxis"][taxi]["fuel"] > 0:
#                 current_actions.append((("move", taxi, (taxi_loc[0] + 1, taxi_loc[1])), (taxi_loc[0] + 1, taxi_loc[1])))
#                 current_actions.append((("move", taxi, (taxi_loc[0], taxi_loc[1] + 1)), (taxi_loc[0], taxi_loc[1] + 1)))
#                 current_actions.append((("move", taxi, (taxi_loc[0], taxi_loc[1] - 1)), (taxi_loc[0], taxi_loc[1] - 1)))
#                 current_actions.append((("move", taxi, (taxi_loc[0] - 1, taxi_loc[1])), (taxi_loc[0] - 1, taxi_loc[1])))
#
#             list_to_remove = []
#             for act in current_actions:
#                 if act[0][2][0] < 0 or act[0][2][1] < 0 or act[0][2][0] > len(self.map) - 1 or act[0][2][1] > \
#                         len(self.map[0]) - 1 or self.map[act[0][2][0]][act[0][2][1]] == "I":
#                     list_to_remove.append(act)
#
#             for act in list_to_remove:
#                 current_actions.remove(act)
#
#             actions_taxi[taxi] = current_actions
#
#             for name in passengers:
#                 if state["passengers"][name]["location"] == taxi_loc and state["passengers"][name]["taxi"] != taxi:
#                     actions_taxi[taxi].append((("pick up", taxi, name), taxi_loc))
#
#             for name_in_taxi in state["taxis"][taxi]["passengers_names"]:
#                 if state["passengers"][name_in_taxi]["location"] == self.const_passengers[name_in_taxi]["destination"]:
#                     actions_taxi[taxi].append((("drop off", taxi, name_in_taxi), taxi_loc))
#
#             if "G" == self.map[taxi_loc[0]][taxi_loc[1]]:
#                 actions_taxi[taxi].append((("refuel", taxi), taxi_loc))
#
#             actions_taxi[taxi].append((("wait", taxi), taxi_loc))  # ("move", "taci_2", (2,1))
#         actions = list(itertools.product(*actions_taxi.values()))
#         possible_actions = []
#         for act in actions:
#             loc_in_act = set([loc[1] for loc in act])
#
#             if len(loc_in_act) == self.num_taxis:
#                 possible_actions.append(tuple([loc[0] for loc in act]))
#         return tuple(possible_actions)
#
#     def result(self, state, action):
#         """Return the state that results from executing the given
#         action in the given state. The action must be one of
#         self.actions(state)."""
#         state = ast.literal_eval(state)
#         new_state = deepcopy(state)
#
#         if action == ():
#             new_state = (-2, -2, None)
#
#         for act in action:
#             if act[0] == "move":
#                 new_state["taxis"][act[1]]["location"] = act[2]
#                 new_state["taxis"][act[1]]["fuel"] -= 1
#                 for name in state["taxis"][act[1]]["passengers_names"]:
#                     new_state["passengers"][name]["location"] = act[2]
#
#             if act[0] == "pick up":
#                 new_state["taxis"][act[1]]["capacity"] += 1
#                 new_state["taxis"][act[1]]["passengers_names"].append(act[2])
#                 new_state["passengers"][act[2]]["taxi"] = act[1]
#
#             if act[0] == "drop off":
#                 new_state["taxis"][act[1]]["capacity"] -= 1
#                 new_state["taxis"][act[1]]["passengers_names"].remove(act[2])
#                 new_state["passengers"][act[2]]["taxi"] = "none"
#
#             if act[0] == "refuel":
#                 new_state["taxis"][act[1]]["fuel"] = self.const_taxis[act[1]]["fuel"]
#
#         return str(new_state)
#
#     def goal_test(self, state):
#         """ Given a state, checks if this is the goal state.
#          Returns True if it is, False otherwise."""
#
#         state = ast.literal_eval(state)
#         for name in state["passengers"].keys():
#             if state["passengers"][name]["location"] != self.const_passengers[name]["destination"] or \
#                     state["passengers"][name]["taxi"] != "none":
#                 return False
#         return True
#
#     def h(self, node):
#         """ This is the heuristic. It gets a node (not a state,
#         state can be accessed via node.state)
#         and returns a goal distance estimate"""
#         return 0
#
#     def h_1(self, node):
#         """
#         This is a simple heuristic
#         """
#         node_state = ast.literal_eval(node.state)
#         heuristic_estimiation = 0
#         for name in node_state["passengers"].keys():
#             if node_state["passengers"][name]["taxi"] == "none":
#                 heuristic_estimiation += 2
#             else:
#                 heuristic_estimiation += 1
#
#         return heuristic_estimiation / self.num_taxis
#
#     def h_2(self, node):
#         """
#         This is a slightly more sophisticated Manhattan heuristic
#         """
#         node_state = ast.literal_eval(node.state)
#         DT = 0
#         for name in node_state["passengers"].keys():
#             DT += math.abs(
#                 node_state["passengers"][name]["location"][0] - self.const_passengers[name]["destination"][0])
#             DT += math.abs(
#                 node_state["passengers"][name]["location"][1] - self.const_passengers[name]["destination"][1])
#
#         return DT / self.num_taxis
#
#     """Feel free to add your own functions
#     (-2, -2, None) means there was a timeout"""
#
#
# def create_taxi_problem(game):
#     return TaxiProblem(game)
