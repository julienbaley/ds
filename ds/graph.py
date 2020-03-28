import tempfile
from collections import Counter
from html import unescape
from itertools import chain, filterfalse
from operator import itemgetter

import matplotlib
import matplotlib.pyplot as plt
import networkx as nx
from igraph import Graph
from tqdm import tqdm

from .helpers import window_combinations

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


def get_non_community_edges(nx_graph, communities):
    # retrieve all communities edges
    comm_edges = (get_community_graph(nx_graph, community).edges
                  for community in communities)
    comm_edges = set(map(tuple, map(sorted, chain.from_iterable(comm_edges))))

    # then go through the graph edges and filter out the community edges
    return list(filterfalse(comm_edges.__contains__,
                            map(tuple, map(sorted, nx_graph.edges))))


def keep_only_communities(nx_graph, communities):
    non_comm_edges = get_non_community_edges(nx_graph, communities)

    # remove any edge from the graph that isn't in a community
    ret = nx_graph.copy()
    ret.remove_edges_from(non_comm_edges)
    return ret


def get_community_graph(nx_graph, community):
    return nx_graph.subgraph(community).copy()


def plot(nx_graph, mapping_fun=lambda c: c, communities=None,
         use_community_layout=True):

    if communities is None:
        communities = [nx_graph.nodes]  # a single community with all nodes

    # establish the layout of the nodes
    pos = nx.spring_layout(keep_only_communities(nx_graph, communities)
                           if use_community_layout
                           else nx_graph)

    # for each community
    for i, comm in enumerate(communities):
        # draw the nodes of the community
        nx.draw_networkx_nodes(
            nx_graph, pos,
            nodelist=comm,
            node_color=f'C{i}',  # in a different colour
            node_size=500,
            alpha=0.8)

        # draw the edges of the community
        nx.draw_networkx_edges(
            nx_graph, pos,
            edgelist=get_community_graph(nx_graph, comm).edges,
            edge_color=f'C{i}')

    # draw all other edges in a single colour
    nx.draw_networkx_edges(
        nx_graph, pos,
        edgelist=get_non_community_edges(nx_graph, communities),
        alpha=0.5,
        edge_color='grey')

    # write the characters in each node
    mapping = dict(zip(nx_graph, map(mapping_fun, nx_graph)))
    nx.draw_networkx_labels(
        nx_graph, pos,
        font_color='w',
        labels=mapping,
        font_family=FONT)

    plt.show()
