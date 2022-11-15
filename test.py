
state = {
            "map": [['P', 'P', 'P', 'P'],
                    ['P', 'P', 'P', 'P'],
                    ['P', 'I', 'G', 'P'],
                    ['P', 'P', 'P', 'P'], ],
            "taxis": {'taxi 1': {"location": (3, 3),
                                 "fuel": 15,
                                 "capacity": 2},
                      'taxi 2': {"location": (3, 3),
                                 "fuel": 15,
                                 "capacity": 2}
                      },

            "passengers": {'Yossi': {"location": (2, 3),
                                     "destination": (2, 3)},
                           'Moshe': {"location": (1, 0),
                                     "destination": (0, 0)}
                           }
        }


def dict_to_tuples(state):
    res = []
    if type(state) == list and type(state[0]) == list:
        r = []
        for l in state:
            r.append(tuple(l))
        return tuple(r)
    if type(state) != dict:
        return state
    for key in sorted(list(state.keys())):
        res.append((key, dict_to_tuples(state[key])))
    return tuple(res)



t = dict_to_tuples(state)


def tuple_to_dict(state):
    a = {}
    p = {}
    q = {}

    a[state[0][0]] = state[0][1]
    a[state[1][0]] = p
    pasgs = state[1][1]
    for t in pasgs:
        p[t[0]] = {t[1][0][0]: t[1][0][1], t[1][1][0]: t[1][1][1]}
    a[state[2][0]] = q # {taxis : {}}
    for taxi in state[2][1]:


    return None

print(tuple_to_dict(t))

