import numpy as np
from collections import deque

class PetriNet:
    def __init__(self, place_names, transition_data):
        """place_names: list of strings
        transition_data: dict like {transition: (inputs, outputs)}
            where inputs/outputs are {place: weight}"""
        self.place_names = place_names
        self.place_to_idx = {name: i for i, name in enumerate(place_names)}
        self.n_places = len(place_names)
        
        self.transitions = {}
        for name, (ins, outs) in transition_data.items():
            in_vec = np.zeros(self.n_places, dtype=float)
            out_vec = np.zeros(self.n_places, dtype=float)
            for p, w in ins.items(): in_vec[self.place_to_idx[p]] = w
            for p, w in outs.items(): out_vec[self.place_to_idx[p]] = w
            self.transitions[name] = (in_vec, out_vec - in_vec)

class Node:
    def __init__(self, marking, parent=None):
        self.marking = tuple(marking)
        self.parent = parent
        self.children = {} # {transition: Node}

class KarpMillerTree:
    def __init__(self, net, initial_marking_dict):
        """net: PetriNet instance
        initial_marking_dict: dict like {place: tokens}"""
        self.net = net
        init_marking = np.zeros(net.n_places, dtype=float) # store markings as np arrays
        for p, v in initial_marking_dict.items():               # for quick vector operations
            init_marking[net.place_to_idx[p]] = v
            
        self.root = Node(init_marking)
        self.nodes = {self.root.marking: self.root}
        self._build(self.root)

    def _get_ancestors(self, node):
        """internal helper. returns the strict ancestors of node"""
        curr = node
        while curr is not None:
            yield curr
            curr = curr.parent

    def _build(self, root_node):
        """internal helper. builds the karp-miller tree"""
        queue = deque([root_node])
        
        while queue:
            curr_node = queue.popleft()
            curr_m = np.array(curr_node.marking) # convert marking to np array

            for t, (in_vec, delta) in self.net.transitions.items():
                if np.all(curr_m >= in_vec): # check if t is enabled
                    next_m = curr_m + delta
                    
                    # karp-miller acceleration
                    # for every strict ancestor of next_m it covers, mark places 
                    # where next_m has strictly more tokens with omega
                    for ancestor in self._get_ancestors(curr_node):
                        anc_m = np.array(ancestor.marking)
                        if np.all(next_m >= anc_m) and np.any(next_m > anc_m): # if next_m covers anc_m
                            next_m[next_m > anc_m] = np.inf 
                    
                    next_m_tuple = tuple(next_m) # convert back to tuple
                    
                    # do not duplicate nodes
                    if next_m_tuple not in self.nodes:
                        new_node = Node(next_m, parent=curr_node)
                        self.nodes[next_m_tuple] = new_node
                        curr_node.children[t] = new_node
                        queue.append(new_node)
                    else:
                        curr_node.children[t] = self.nodes[next_m_tuple]

    def search(self, predicate, return_path=False):
        """searches the karp-miller tree for a marking that satisfies predicate
            predicate: function that takes a dict {place: tokens} and returns a Boolean.
            return_path: if true, return path to marking as well"""
        results = []
        for marking_tuple, node in self.nodes.items():
            # convert tuple to dict
            marking_dict = {
                self.net.place_names[i]: val 
                for i, val in enumerate(marking_tuple)
            }
            if predicate(marking_dict): # check if marking satisfies predicate
                if return_path:
                    # reconstruct path by backtracking
                    path = []
                    curr = node
                    while curr.parent is not None:
                        for t, child in curr.parent.children.items():
                            if child == curr:
                                path.append(t)
                                break
                        curr = curr.parent
                    results.append((marking_tuple, path[::-1])) # reverse path
                else:
                    results.append(marking_tuple)
        return results
    
    def print_tree(self, node=None, prefix="", is_last=True, visited=None):
        """recursively prints the karp-miller tree with ASCII formatting."""
        # base case
        if visited is None:
            visited = set()
            node = self.root
            print(f"Place order: {self.net.place_names}") # for reference
            print(f"{self._format_marking(node.marking)}") # root node
            visited.add(node.marking)

        # print children 
        child_items = list(node.children.items())
        for i, (trans, child_node) in enumerate(child_items):
            # formatting logic
            is_child_last = (i == len(child_items) - 1)
            branch = "└── " if is_child_last else "├── "
            
            marking_str = self._format_marking(child_node.marking)
            
            # check if child already printed
            if child_node.marking in visited:
                print(f"{prefix}{branch}[{trans}] ──> {marking_str} (backlink)")
                continue # do not recurse
                
            # print child
            print(f"{prefix}{branch}[{trans}] ──> {marking_str}")
            visited.add(child_node.marking)
            
            # recurse
            next_prefix = prefix + ("    " if is_child_last else "│   ")
            self.print_tree(child_node, next_prefix, is_child_last, visited)

    def _format_marking(self, marking):
        """internal helper. converts marking to a list of string,
        using "w" to represent np.inf"""
        readable = [str(int(v)) if v != np.inf else "w" for v in marking]
        return f"({', '.join(readable)})"