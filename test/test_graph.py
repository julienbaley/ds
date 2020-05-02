import unittest
from collections import Counter

from ds import graph
from ds.poem import Poem


class TestGraph(unittest.TestCase):
    def setUp(self):
        self.poem = ['國破山河在，城春草木深。',
                     '感時花濺淚，恨別鳥驚心。',
                     '峰火連三月，家書抵萬金。',
                     '白頭搔更短，渾欲不勝簪。']
        self.poem = Poem({'paragraphs': self.poem})

    @staticmethod
    def grouping_fun(p):
        return [Poem.get_rhymes(p)]

    def test_build_single_poem_graph(self):
        nodes, edges = graph.build_single_poem_graph(self.poem,
                                                     self.grouping_fun)

        N = {k: graph.Node(k, k) for k in '深心金簪'}
        self.assertEquals(Counter(map(N.get, '深心金簪')), nodes)
        self.assertEquals(Counter({(N['簪'], N['金']): 1,
                                   (N['心'], N['深']): 1,
                                   (N['心'], N['簪']): 1,
                                   (N['心'], N['金']): 1,
                                   (N['深'], N['金']): 1,
                                   (N['深'], N['簪']): 1}),
                          edges)

    def test_build_python_graph(self):
        p_nodes, p_edges = graph.build_single_poem_graph(self.poem,
                                                         self.grouping_fun)
        # we build a corpus of twice the same poem
        nodes, edges = graph.build_python_graph([self.poem, self.poem],
                                                self.grouping_fun)
        self.assertEquals(p_nodes + p_nodes, nodes)
        self.assertEquals(p_edges + p_edges, edges)

    def test_py2nx(self):
        nodes, edges = graph.build_single_poem_graph(self.poem,
                                                     self.grouping_fun)
        gph = graph.py2nx(nodes, edges)
        for node, data in gph.nodes(data=True):
            self.assertEquals(nodes[node], data['weight'])
        for a, b, data in gph.edges(data=True):
            self.assertEquals(edges[tuple(sorted((a, b)))], data['weight'])

        self.assertEquals(len(nodes), len(gph.nodes))
        self.assertEquals(len(edges), len(gph.edges))


class TestCommunities(unittest.TestCase):
    def setUp(self):
        self.nodes = {'a': 10, 'wa': 5, 'ia': 5, 'e': 10, 'ie': 5}
        self.edges = {('a', 'wa'): 4,
                      ('a', 'ia'): 4,
                      ('wa', 'ia'): 1,
                      ('e', 'ie'): 5,
                      # although there is a link, it is weak (weight=1) and
                      # only between 2 nodes of the 'a' and 'e' communities
                      ('a', 'e'): 1,
                      }

    def test_get_communities(self):
        nx = graph.py2nx(self.nodes, self.edges)
        comms = graph.get_communities(nx)
        self.assertEquals(sorted([frozenset({'a', 'wa', 'ia'}),
                                  frozenset({'e', 'ie'})]),
                          sorted(comms))

    def test_keep_only_communities(self):
        nx = graph.py2nx(self.nodes, self.edges)
        comms = graph.get_communities(nx)
        nx = graph.keep_only_communities(nx, comms)

        self.assertNotIn(('a', 'e'), nx.edges)
        for edge in set(self.edges.keys()) - {('a', 'e')}:
            self.assertIn(edge, nx.edges)

    def test_get_community_graph(self):
        nx = graph.py2nx(self.nodes, self.edges)
        comms = graph.get_communities(nx)

        for comm in comms:
            subgph = graph.get_community_graph(nx, comm)
            self.assertEquals(comm, set(subgph.nodes))


class TestAssortativity(unittest.TestCase):
    def setUp(self):
        self.Nodes = {1: graph.Node(1, 'blue'),
                      2: graph.Node(2, 'blue'),
                      3: graph.Node(3, 'blue'),
                      4: graph.Node(4, 'red'),
                      5: graph.Node(5, 'red'),
                      6: graph.Node(6, 'red'),
                      }

    def test_assortativity_1(self):
        nodes = {k: 1 for k in self.Nodes.values()}
        N = self.Nodes
        edges = {(N[1], N[2]): 1,
                 (N[1], N[3]): 1,
                 (N[2], N[3]): 1,
                 (N[3], N[4]): 1,
                 (N[4], N[5]): 1,
                 (N[4], N[6]): 1,
                 (N[5], N[6]): 1,
                 }
        nx = graph.py2nx(nodes, edges)
        self.assertAlmostEqual(0.71,
                               graph.get_assortativity(nx),
                               places=2)

    def test_assortativity_2(self):
        nodes = {k: 1 for k in self.Nodes.values()}
        N = self.Nodes
        edges = {(N[1], N[2]): 1,
                 (N[1], N[6]): 1,
                 (N[2], N[3]): 1,
                 (N[3], N[4]): 1,
                 (N[3], N[5]): 1,
                 (N[3], N[6]): 1,
                 (N[4], N[5]): 1,
                 (N[4], N[6]): 1,
                 (N[5], N[6]): 1,
                 }
        nx = graph.py2nx(nodes, edges)
        self.assertAlmostEqual(0.1,
                               graph.get_assortativity(nx),
                               places=2)
