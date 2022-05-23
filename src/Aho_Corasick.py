from __future__ import annotations
from random import randint
import matplotlib.pyplot as plt
from networkx import DiGraph, draw_networkx_nodes, draw_networkx_edges, draw_networkx_edge_labels

class AhoCorasick:
    # Character set for DNA
    charset = {
        'A': 0,
        'C': 1,
        'G': 2,
        'T': 3
    }

    # Number of allowed characters
    charset_len = len(charset)

    def __init__(self, words: list[str]) -> None:
        # Neutralize Case in words and remove characters other than ACGT
        self.words = [word.upper() for word in words if not any(char not in self.charset.keys() for char in word.upper())]

        # Get Upper Bound Number of Nodes
        self.max_nodes = sum([len(word) for word in words]) + 1

        # Output Dictionary
        self.out = {
            i: set() for i in range(self.max_nodes) # Set of Output Words
        }

        # Failure Array
        self.fail = [-1] * self.max_nodes

        # Goto Matrix, rows = max_nodes, cols = charset_len
        self.goto = [[-1] * self.charset_len for _ in range(self.max_nodes)]

        # Build Output, Failure, and Goto
        self.nodes = self.__initialize()

    def __initialize(self) -> int:
        # Initial number of nodes (Includes Root Node)
        nodes = 1

        # Assign States
        for word in self.words:
            current_node = 0

            for char in word:
                hash = self.charset[char]

                if self.goto[current_node][hash] == -1:
                    self.goto[current_node][hash] = nodes
                    nodes += 1

                current_node = self.goto[current_node][hash]

            self.out[current_node].add(word)

        # Preparing To Compute Fail Function
        node_q = []

        for hash in range(self.charset_len):
            node = self.goto[0][hash]
            if node != -1:
                self.fail[node] = 0
                node_q.append(node)
            else:
                self.goto[0][hash] = 0

        # Compute Fail Function
        while node_q:
            parent_node = node_q.pop(0)

            for hash in range(self.charset_len):
                current_node = self.goto[parent_node][hash]
                if current_node != -1:
                    fallback_node = self.fail[parent_node]

                    while self.goto[fallback_node][hash] == -1:
                        fallback_node = self.fail[fallback_node]
                    fallback_node = self.goto[fallback_node][hash]

                    self.fail[current_node] = fallback_node
                    self.out[current_node].union(self.out[fallback_node])
                    node_q.append(current_node)

        return nodes

    # Private Get Position Function
    def __getpos(self, current_node, depth, pos):
        count = 0
        for hash in range(self.charset_len):
            next_node = self.goto[current_node][hash]
            if next_node != -1 and next_node != 0:
                if count > 0:
                    depth -= 10
                pos[next_node] = (pos[current_node][0] + 10, depth)
                depth, pos = self.__getpos(next_node, depth, pos)
                count += 1
        return depth, pos

    # Visualization using Networkx Digraph
    def visualize(self) -> None:
        dg = DiGraph()

        pos = {0: (0, 0)}
        _, pos = self.__getpos(0, 0, pos)

        edge_labels = dict()
        dg.add_node(0)
        for i, row in enumerate(self.goto):
            for j, col in enumerate(row):
                if col != 0 and col != -1:
                    dg.add_node(col)
                    dg.add_edge(i, col)
                    edge_labels[(i, col)] = "ACGT"[j]
        draw_networkx_nodes(dg, pos, node_size=100, node_color="red")
        draw_networkx_edge_labels(dg, pos, edge_labels=edge_labels, font_size=8)
        draw_networkx_edges(dg, pos, alpha=0.5)

        node_list = list()
        for key, value in self.out.items():
            if value:
                node_list.append(key)
        draw_networkx_nodes(dg, pos, nodelist=node_list, node_size=100, node_color="green")
        draw_networkx_nodes(dg, pos, nodelist=[0], node_size=200, node_color="blue")

        edge_list = list()
        for i in range(self.max_nodes):
            if self.fail[i] != -1 and self.fail[i] != 0:
                dg.add_edge(i, self.fail[i])
                edge_list.append((i, self.fail[i]))
        draw_networkx_edges(dg, pos, edgelist=edge_list, edge_color="green", connectionstyle="arc3, rad=-0.3", alpha=0.3)

        plt.show()

    # Node Traversal Using Goto and Fail Functions
    def __get_next_node(self, ref_node: int, input: str) -> int:
        current_node = ref_node
        hash = self.charset[input]

        next_node = self.goto[current_node][hash]
        while next_node == -1:
            current_node = self.fail[current_node]
            next_node = self.goto[current_node][hash]

        return next_node

    # Search for initialized strings in text body, returns dictionary of words and indices
    def search_in_sequence(self, body: str) -> dict:
        sequence = body.upper()

        result: dict[list[tuple]] = dict()

        current_node = 0
        for i in range(len(sequence)):
            current_node = self.__get_next_node(current_node, sequence[i])

            if self.out[current_node]:
                for word in self.out[current_node]:
                    if result.get(word):
                        result[word].append(i - len(word) + 1)
                    else:
                        result[word] = [i - len(word) + 1]

        return result

def getRandomGenomes(length: int = 8, frequency: int = 10) -> list[str]:
    words = list()
    for _ in range(frequency):
        words.append("".join("ACGT"[randint(0, 3)] for _ in range(length)))
    return words

def getRandomBody(length: int = 10000) -> str:
    return "".join("ACGT"[randint(0, 3)] for _ in range(length))

# Driver Using Randomness
if __name__ == "__main__":
    words = getRandomGenomes()
    text = getRandomBody()
    aho = AhoCorasick(words)
    print(aho.search_in_sequence(text))
    aho.visualize()