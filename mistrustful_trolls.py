from pynode.main import *
from typing import List, Set
from itertools import combinations
from functools import partial, partialmethod


class Entity:
    def __init__(self, name):
        self.class_name = "entity"
        self.name = name

    def __str__(self):
        return str(self.class_name)[0] + str(self.name)


class Goat(Entity):
    def __init__(self, name):
        Entity.__init__(self, name)
        self.troll = None
        self.class_name = "goat"


class Troll(Entity):
    def __init__(self, name):
        Entity.__init__(self, name)
        self.goat = None
        self.class_name = "troll"


class Land:
    def __init__(self, contents: Set[Entity]):
        self.contents = contents

    def is_valid(self):
        goats = set(self.get_goats(self.contents))
        trolls = set(self.get_trolls(self.contents))

        for goat in goats:
            if not trolls.issuperset({goat.troll}) and len(trolls) != 0:
                return False

        return True

    def generate_boat_permutations(self, original_state):
        # Curry self.is_permutation_valid with the original state.
        valid_combination = partial(self.is_permutation_valid, original_state=original_state)

        return list(filter(valid_combination, list(combinations(self.contents, 2)))) + list(map(lambda x: {x}, self.contents))

    def create_node(self):
        graph_text = ""
        for i in self.contents:
            graph_text += str(i) + "\n"

        node = graph.add_node(id=self, value=graph_text)

        if len(self.contents) == 0:
            node.set_attribute("empty", True)

        return node

    def is_permutation_valid(self, permutation, original_state):
        goats = set(self.get_goats(permutation))
        trolls = set(self.get_trolls(permutation))

        # Check to make sure that the troll isn't crossing the river with a goat it doesn't own
        # The problem specification states 'no goat is left in the company of any other troll without the goat's owner
        # also being present'.

        #for goat in goats:
        #    if not trolls.issuperset({goat.troll}):
        #        return False

        # Check to make sure that a troll isn't leaving its goat with another troll
        # i.e for each troll in 'trolls' check that their goat is either in 'goats'
        # or it is not left behind on land with another troll.

        for troll in trolls:
            # More than 0 trolls on the land, the goat isn't in the boat and the land contains the goat
            if len(set(self.get_trolls(self.contents)).difference(trolls)) > 0 and not goats.issuperset({troll.goat}) and self.contents.issuperset({troll.goat}):
                return False

        # Check that the goat isn't leaving its troll to go to the other side where there is a troll which
        # does not own it.

        far_side_contents = original_state.contents.difference(self.contents)
        far_side_trolls = set(self.get_trolls(far_side_contents))
        far_side_goats = set(self.get_goats(far_side_contents))

        for goat in goats:
            if len(far_side_trolls) > 0 and not set(far_side_trolls).issuperset({goat.troll}) and not trolls.issuperset({goat.troll}):
                return False

        # Check that the troll isn't going to the other side where there is a goat that it doesn't own, and there is
        # no owner nearby.

        for goat in far_side_goats:
            if len(trolls) > 0 and not trolls.issuperset({goat.troll}) and not far_side_trolls.issuperset({goat.troll}):
                return False

        return True

    @staticmethod
    def get_entity_type(iterable, class_name):
        return filter(lambda ent: ent.class_name == class_name, iterable)

    get_trolls = partialmethod(get_entity_type, class_name="troll")
    get_goats = partialmethod(get_entity_type, class_name="goat")


def create_troll_goat_pair(name):

    goat = Goat(str(name))
    troll = Troll(str(name))

    goat.troll = troll
    troll.goat = goat

    return troll, goat


def start():
    trolls = []
    goats = []

    for i in range(3):
        troll, goat = create_troll_goat_pair(i)
        trolls.append(troll)
        goats.append(goat)

    original_state = Land(set(trolls).union(set(goats)))
    original_node = original_state.create_node()
    original_node.set_attribute("boat", True)
    original_node.set_color(Color.rgb(0, 0, 255))

    next_state(original_state, original_state, original_node)

    found = True
    while found:
        found = False
        for i in graph.nodes():
            if not i.attribute("empty") and len(i.outgoing_edges()) == 0:
                graph.remove_node(i)
                found = True


def next_state(original_state, prev_state, prev_node, has_boat=True):
    if has_boat:
        next_even_state(original_state, prev_state, prev_node, has_boat)
    else:
        next_odd_state(original_state, prev_state, prev_node, has_boat)


def next_even_state(original_state, prev_state, prev_node, has_boat):
    for i in prev_state.generate_boat_permutations(original_state):

        new_land = Land(prev_state.contents.difference(set(i)))

        found_duplicate = False

        for node in graph.nodes():
            if node.id().contents == new_land.contents and not node.attribute("boat") and not node.attribute("empty"):
                found_duplicate = True
                break

        if found_duplicate:
            continue

        if new_land.is_valid():
            new_node = new_land.create_node()
            graph.add_edge(prev_node, new_node, directed=True)
            if not new_node.attribute("empty"):
                next_state(original_state, new_land, new_node, not has_boat)


def next_odd_state(original_state, prev_state, prev_node, has_boat):
    far_land = Land(original_state.contents.difference(prev_state.contents))

    if not far_land.is_valid():
        cur_node = prev_node
        while len(cur_node.outgoing_edges()) == 1:
            temp = cur_node.outgoing_edges()[0]
            graph.remove_node(cur_node)
            cur_node = temp

        return

    for i in far_land.generate_boat_permutations(original_state):
        new_land = Land(prev_state.contents.union(set(i)))

        found_duplicate = False

        for node in graph.nodes():
            if node.id().contents == new_land.contents and node.attribute("boat") and not node.attribute("empty"):
                found_duplicate = True
                break

        if found_duplicate:
            continue

        if new_land.is_valid():
            new_node = new_land.create_node()
            new_node.set_attribute("boat", True)
            new_node.set_color(Color.rgb(0, 0, 255))
            graph.add_edge(prev_node, new_node, directed=True)

            if not new_node.attribute("empty"):
                next_state(original_state, new_land, new_node, not has_boat)


begin_pynode(start)
