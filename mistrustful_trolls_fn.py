import functools
import itertools
import operator

NUM_TROLLS = 3
initial_state = ("t1", "t2", "t3",  # Trolls
                 "g1", "g2", "g3")  # Goats


def get_next_states(current_state):
    return tuple(itertools.combinations(current_state, 2)) + tuple(itertools.combinations(current_state, 1))

print(get_next_states(initial_state))

# Assume each troll has a goat

def get_troll(goat):
    return "t" + str(goat[1:])

def get_goat(troll):
    return "g" + str(troll[1:])


def is_state_valid(potential_state, seen_states):
    trolls = tuple(filter(lambda x: operator.contains(x, "t"), potential_state))
    goats = tuple(filter(lambda x: operator.contains(x, "g"), potential_state))

    # Check if all trolls have their goats
    functools.reduce(operator.and_, map(lambda troll: functools.reduce(operator.or_, map(lambda goat: goat == get_goat(troll), goats)), trolls))


    return not operator.contains(seen_states, potential_state)

    # There must not be a troll present anywhere with a goat that it does not own, while the goat's owner is also not
    # present




def create_graph(current_state, seen_states):
    is_valid = functools.partial(is_state_valid, seen_state=seen_states)
    potential_states = filter(is_valid, map(get_next_states(current_state)))

    for state in potential_states:
        return create_graph(state, seen_states + tuple([state]))