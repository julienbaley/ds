import unittest
from collections import Counter
from operator import itemgetter

from ds import graph
from ds.poem import Poem


class TestGraph(unittest.TestCase):
    def setUp(self):
        self.poem = ['國破山河在，城春草木深。',
                     '感時花濺淚，恨別鳥驚心。',
                     '峰火連三月，家書抵萬金。',
                     '白頭搔更短，渾欲不勝簪。']
        self.prons = {
            '深': [{'GY Rhyme': '侵'}, {'GY Rhyme': '沁'}],
            '心': [{'GY Rhyme': '侵'}],
            '金': [{'GY Rhyme': '侵'}],
            '簪': [{'GY Rhyme': '侵'}, {'GY Rhyme': '覃'}],
        }
        self.poem = Poem({'paragraphs': self.poem, 'prons': self.prons})

    def test_build_single_poem_graph(self):
        nodes, edges = graph.build_single_poem_graph(self.poem)

        N = {k: graph.Node(k, '侵') for k in '深心金簪'}
        self.assertEquals(Counter(map(N.get, '深心金簪')), nodes)
        self.assertEquals(Counter({(N['簪'], N['金']): 1,
                                   (N['心'], N['深']): 1,
                                   (N['心'], N['簪']): 1,
                                   (N['心'], N['金']): 1,
                                   (N['深'], N['金']): 1,
                                   (N['深'], N['簪']): 1}),
                          edges)

    def test_build_python_graph(self):
        p_nodes, p_edges = graph.build_single_poem_graph(self.poem)
        # we build a corpus of twice the same poem
        nodes, edges = graph.build_python_graph([self.poem, self.poem])
        self.assertEquals(p_nodes + p_nodes, nodes)
        self.assertEquals(p_edges + p_edges, edges)

    def test_py2nx(self):
        nodes, edges = graph.build_single_poem_graph(self.poem)
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
        N = {1: graph.Node(1, 'blue'),
             2: graph.Node(2, 'blue'),
             3: graph.Node(3, 'blue'),
             4: graph.Node(4, 'red'),
             5: graph.Node(5, 'red'),
             6: graph.Node(6, 'red'),
             }
        nodes = {k: 1 for k in N.values()}
        # 123 together, 456 together, 3-4 bridge
        edges1 = {(N[1], N[2]): 1,
                  (N[1], N[3]): 1,
                  (N[2], N[3]): 1,
                  (N[3], N[4]): 1,
                  (N[4], N[5]): 1,
                  (N[4], N[6]): 1,
                  (N[5], N[6]): 1,
                  }
        # 3456 together, 1-2, 1-6, 2-3, 2-6
        edges2 = {(N[1], N[2]): 1,
                  (N[1], N[6]): 1,
                  (N[2], N[3]): 1,
                  (N[2], N[6]): 1,
                  (N[3], N[4]): 1,
                  (N[3], N[5]): 1,
                  (N[3], N[6]): 1,
                  (N[4], N[5]): 1,
                  (N[4], N[6]): 1,
                  (N[5], N[6]): 1,
                  }
        # each blue links to all red, no other links
        edges3 = {(N[1], N[4]): 1,
                  (N[1], N[5]): 1,
                  (N[1], N[6]): 1,
                  (N[2], N[4]): 1,
                  (N[2], N[5]): 1,
                  (N[2], N[6]): 1,
                  (N[3], N[4]): 1,
                  (N[3], N[5]): 1,
                  (N[3], N[6]): 1,
                  }

        self.assort_nx = graph.py2nx(nodes, edges1)
        self.less_assort_nx = graph.py2nx(nodes, edges2)
        self.not_assort_nx = graph.py2nx(nodes, edges3)

    def test_assortativity(self):
        self.assertAlmostEqual(0.71,
                               graph.get_assortativity(self.assort_nx),
                               places=2)
        self.assertAlmostEqual(0,
                               graph.get_assortativity(self.less_assort_nx),
                               places=1)
        self.assertAlmostEqual(-1,
                               graph.get_assortativity(self.not_assort_nx),
                               places=2)

    def test_shuffle(self):
        nx = self.assort_nx
        nx_shuffled = graph.shuffle(nx)

        def iter_rimes(nx_graph):
            return map(itemgetter('rime'),
                       map(itemgetter(1),
                           nx_graph.nodes(data=True)))

        self.assertEquals(Counter(iter_rimes(nx)),
                          Counter(iter_rimes(nx_shuffled)))

        self.assertEquals(set(nx.nodes), set(nx_shuffled.nodes))
        self.assertEquals(nx.edges, nx_shuffled.edges)

        self.assertNotEquals(graph.get_assortativity(nx),
                             graph.get_assortativity(nx_shuffled))

    def test_pval_sigma(self):
        pval_ass, sigma_ass = graph.get_pval_sigma(self.assort_nx)
        pval_less, sigma_less = graph.get_pval_sigma(self.less_assort_nx)
        pval_not, sigma_not = graph.get_pval_sigma(self.not_assort_nx)

        self.assertLess(pval_ass, pval_less)
        self.assertLess(pval_less, pval_not)

        self.assertGreater(sigma_ass, sigma_less)
        self.assertGreater(sigma_less, sigma_not)
