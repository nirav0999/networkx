import pytest

import networkx as nx
from networkx.algorithms.community import (
    greedy_modularity_communities,
    naive_greedy_modularity_communities,
)


@pytest.mark.parametrize(
    "func", (greedy_modularity_communities, naive_greedy_modularity_communities)
)
def test_modularity_communities(func):
    G = nx.karate_club_graph()
    john_a = frozenset(
        [8, 14, 15, 18, 20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33]
    )
    mr_hi = frozenset([0, 4, 5, 6, 10, 11, 16, 19])
    overlap = frozenset([1, 2, 3, 7, 9, 12, 13, 17, 21])
    expected = {john_a, overlap, mr_hi}
    assert set(func(G)) == expected


@pytest.mark.parametrize(
    "func", (greedy_modularity_communities, naive_greedy_modularity_communities)
)
def test_modularity_communities_categorical_labels(func):
    # Using other than 0-starting contiguous integers as node-labels.
    G = nx.Graph(
        [
            ("a", "b"),
            ("a", "c"),
            ("b", "c"),
            ("b", "d"),  # inter-community edge
            ("d", "e"),
            ("d", "f"),
            ("d", "g"),
            ("f", "g"),
            ("d", "e"),
            ("f", "e"),
        ]
    )
    expected = {frozenset({"f", "g", "e", "d"}), frozenset({"a", "b", "c"})}
    assert set(func(G)) == expected


def test_greedy_modularity_communities_relabeled():
    # Test for gh-4966
    G = nx.balanced_tree(2, 2)
    mapping = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"}
    G = nx.relabel_nodes(G, mapping)
    expected = [frozenset({"e", "d", "a", "b"}), frozenset({"c", "f", "g"})]
    assert greedy_modularity_communities(G) == expected


def test_modularity_communities_weighted():
    G = nx.balanced_tree(2, 3)
    for (a, b) in G.edges:
        if ((a == 1) or (a == 2)) and (b != 0):
            G[a][b]["weight"] = 10.0
        else:
            G[a][b]["weight"] = 1.0

    expected = [{0, 1, 3, 4, 7, 8, 9, 10}, {2, 5, 6, 11, 12, 13, 14}]

    assert greedy_modularity_communities(G, weight="weight") == expected


def test_resolution_parameter_impact():
    G = nx.barbell_graph(5, 3)

    gamma = 1
    expected = [frozenset(range(5)), frozenset(range(8, 13)), frozenset(range(5, 8))]
    assert greedy_modularity_communities(G, resolution=gamma) == expected
    assert naive_greedy_modularity_communities(G, resolution=gamma) == expected

    gamma = 2.5
    expected = [{0, 1, 2, 3}, {9, 10, 11, 12}, {5, 6, 7}, {4}, {8}]
    assert greedy_modularity_communities(G, resolution=gamma) == expected
    assert naive_greedy_modularity_communities(G, resolution=gamma) == expected

    gamma = 0.3
    expected = [frozenset(range(8)), frozenset(range(8, 13))]
    assert greedy_modularity_communities(G, resolution=gamma) == expected
    assert naive_greedy_modularity_communities(G, resolution=gamma) == expected


def test_n_communities_parameter():
    G = nx.circular_ladder_graph(4)

    # No aggregation:
    expected = [{k} for k in range(8)]
    assert greedy_modularity_communities(G, n_communities=8) == expected

    # Aggregation to half order (number of nodes)
    expected = [{k, k + 1} for k in range(0, 8, 2)]
    assert greedy_modularity_communities(G, n_communities=4) == expected

    # Default aggregation case (here, 2 communities emerge)
    expected = [frozenset(range(0, 4)), frozenset(range(4, 8))]
    assert greedy_modularity_communities(G, n_communities=1) == expected
