from ex1 import *

state = {
            "map": [['P', 'P', 'P', 'P'],
                    ['P', 'P', 'P', 'P'],
                    ['P', 'I', 'G', 'P'],
                    ['P', 'P', 'P', 'P'], ],
            "taxis": {'taxi 1': {"location": (3, 3),
                                 "fuel": 15,
                                 "max_fuel": 15,
                                 "capacity": 2,
                                 "on_board": ['Yossi', 'Moshe']},
                      'taxi 2': {"location": (3, 3),
                                 "fuel": 15,
                                 "max_fuel": 15,
                                 "capacity": 2,
                                 "on_board": []}
                      },

            "passengers": {'Yossi': {"location": (2, 3),
                                     "destination": (2, 3),
                                     "picked up": False},
                           'Moshe': {"location": (1, 0),
                                     "destination": (0, 0),
                                     "picked up": False}
                           }
        }


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

t = dict_to_tuples(state)

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

print(tuple_to_dict(t))


def actions(state):
    """Returns all the actions that can be executed in the given
    state. The result should be a tuple (or other iterable) of actions
    as defined in the problem description file"""
    if state != dict:
        state = tuple_to_dict(state)
    taxis = state["taxis"]
    passengers = state["passengers"]


    actions = []

    for taxi in taxis:
        wait_flag = True
        for passenger, pos in zip(passengers, local_area(state, taxi)):
            if can_move(state, ("move", taxi, pos)):
                actions.append(("move", taxi, pos))
                wait_flag = False

            if can_pickup(state, ("pick up", taxi, passenger)):
                actions.append(("pick up", taxi, passenger))
                wait_flag = False

            if can_dropoff(state, ("drop off", taxi, passenger)):
                actions.append(("drop off", taxi, passenger))
                wait_flag = False

        if can_refuel(state, ("refuel", taxi)):
            actions.append(("refuel", taxi))
            wait_flag = False
        if wait_flag:
            actions.append(("wait", taxi))

    print(actions)
    return actions

actions(state)

