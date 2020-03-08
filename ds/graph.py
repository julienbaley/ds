import tempfile
from collections import Counter
from html import unescape
from itertools import chain, combinations, filterfalse
from operator import itemgetter

import matplotlib
import matplotlib.pyplot as plt
import networkx as nx
from igraph import Graph
from tqdm import tqdm

FONT = 'Noto Sans CJK TC'
matplotlib.rcParams['font.family'] = FONT


def nx2igraph(nx_graph):
    with tempfile.NamedTemporaryFile(mode='w+') as g:
        temp_gml = g.name
        nx.write_gml(nx_graph, temp_gml)
        ret = Graph.Read_GML(temp_gml)
    for v in ret.vs:
        v['label'] = unescape(v['label'])
    return ret


def window_combinations(lst, wsize):
    '''Slides a window over input and returns the combinations of items in each
    window; typical use cases are wsize=2 which is equivalent to listing the
    windows, and wsize=len(lst) which will give all the combinations of rhymes
    '''
    return set(chain.from_iterable(map(lambda w: list(combinations(w, 2)),
                                       window(lst, wsize))))


def window(lst, n):
    return [lst[i:i+n] for i in range(len(lst)-(n-1))]


def build_single_poem_graph(poem, rhyme_group_fun):
    nodes = Counter()
    edges = Counter()
    for rhyme_group in rhyme_group_fun(poem):
        for c in rhyme_group:
            nodes[c] += 1
        for a, b in window_combinations(rhyme_group, len(rhyme_group)):
            edges[tuple(sorted((a, b)))] += 1

    return nodes, edges


def build_python_graph(poems, rhyme_group_fun):
    nodes = Counter()
    edges = Counter()
    for poem in tqdm(poems):
        poem_nodes, poem_edges = build_single_poem_graph(poem, rhyme_group_fun)
        for n, w in poem_nodes.items():
            nodes[n] += w
        for e, w in poem_edges.items():
            edges[e] += w

    return nodes, edges


def py2nx(nodes, edges):
    ret = nx.Graph()
    for node, weight in nodes.items():
        ret.add_node(node, weight=weight)
    for (a, b), weight in edges.items():
        ret.add_edge(a, b, weight=weight)

    print('Graph done')
    return ret


# public functions


def build_graph(poems, rhyme_group_fun=lambda poem: [poem.get_rhymes()]):
    nodes, edges = build_python_graph(poems, rhyme_group_fun)
    return py2nx(nodes, edges)


def get_communities(nx_graph):
    i_graph = nx2igraph(nx_graph)
    communities = i_graph.community_infomap(edge_weights='weight',
                                            vertex_weights='weight')
    ret = {frozenset(map(itemgetter('label'),
                         map(i_graph.vs.__getitem__, community)))
           for community in communities}
    print('Communities computed')
    return ret


def keep_only_communities(nx_graph, communities):
    # generate every possible edge between nodes of a community
    comm_edges = {tuple(sorted(edge))
                  for community in communities
                  for edge in combinations(community, 2)
                  }

    graph_edges = map(tuple, map(sorted, nx_graph.edges))
    non_comm_edges = list(filterfalse(comm_edges.__contains__, graph_edges))
    # remove any edge from the graph that isn't in a community
    nx_graph.remove_edges_from(non_comm_edges)


def get_community_graph(nx_graph, community):
    return nx_graph.subgraph(community).copy()


def plot(graph, mapping_fun=lambda c: c):
    mapping = dict(zip(graph, map(mapping_fun, graph)))
    print('Mapping:\n', mapping)
    nx.draw(graph,
            font_family=FONT,
            node_size=500,
            with_labels=True,
            font_color='w',
            pos=nx.spring_layout(graph, k=2),
            labels=mapping,
            )

    plt.show()
