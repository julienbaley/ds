import random
import statistics
import tempfile
from collections import Counter, namedtuple
from html import unescape
from itertools import chain, compress, filterfalse, starmap
from operator import itemgetter, methodcaller

import matplotlib
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import networkx as nx
from igraph import Graph
from tqdm import tqdm

from .helpers import annotation_to_selectors, window_combinations
from .community import get_community_label

FONT = 'Noto Sans CJK TC'
matplotlib.rcParams['font.family'] = FONT
Node = namedtuple('Node', ['char', 'rime'], defaults=[''])


def nx2igraph(nx_graph):
    with tempfile.NamedTemporaryFile(mode='w+') as g:
        temp_gml = g.name
        nx.write_gml(nx_graph, temp_gml, stringizer=str)
        ret = Graph.Read_GML(temp_gml)
    for v in ret.vs:
        v['label'] = unescape(v['label'])
    return ret


def build_single_poem_graph(poem, annotator):
    nodes = Counter()
    edges = Counter()
    rhymes = list(starmap(Node, zip(poem.get_rhymes(),
                                    poem.get_rhyme_categories(apply_eq=True))))

    rhyme_groups = [list(compress(rhymes, selector))
                    for selector in annotation_to_selectors(annotator(poem))]

    for node in rhymes:
        nodes[node] += 1
    for rhyme_group in rhyme_groups:
        for a, b in window_combinations(rhyme_group, len(rhyme_group)):
            edges[tuple(sorted((a, b)))] += 1 / max(len(rhyme_group) - 1, 1)

    return nodes, edges


def build_single_poem_graph2(poem):
    nodes = Counter()
    edges = Counter()
    rhymes = [poem.get_rhymes()]
    rhyme_categories = [poem.get_rhyme_categories(apply_eq=True)]

    rhyme_groups = map(lambda x: list(map(lambda y: Node(*y), zip(*x))),
                       zip(rhymes, rhyme_categories))
    for rhyme_group in rhyme_groups:
        for c in rhyme_group:
            nodes[c] += 1
        for a, b in window_combinations(rhyme_group, len(rhyme_group)):
            edges[tuple(sorted((a, b)))] += 1 / max(len(rhyme_group) - 1, 1)

    return nodes, edges


def build_python_graph(poems, annotator):
    nodes = Counter()
    edges = Counter()
    for poem in tqdm(poems):
        poem_nodes, poem_edges = build_single_poem_graph(poem, annotator)
        for n, w in poem_nodes.items():
            nodes[n] += w
        for e, w in poem_edges.items():
            edges[e] += w

    return nodes, edges


def py2nx(nodes, edges):
    ret = nx.Graph()
    for node, weight in nodes.items():
        ret.add_node(node, weight=weight, rime=getattr(node, 'rime', ''))
    for (a, b), weight in edges.items():
        ret.add_edge(a, b, weight=weight)

    print('Graph done')
    return ret


# public functions
def build_manual_graph(edge_list):
    ret = nx.Graph()
    for node in set(chain.from_iterable(edge_list)):
        ret.add_node(node)
    for edge in edge_list:
        ret.add_edge(*edge)
    return ret


def build_graph(poems, annotator=methodcaller('get_naive_annotations')):
    nodes, edges = build_python_graph(poems, annotator)
    return py2nx(nodes, edges)


def get_communities(nx_graph):
    i_graph = nx2igraph(nx_graph)
    communities = i_graph.community_infomap(edge_weights='weight',
                                            vertex_weights='weight')

    def my_eval(s):
        return eval(s) if s.startswith('Node') else s

    ret = [frozenset(map(my_eval,
                         map(itemgetter('label'),
                             map(i_graph.vs.__getitem__, community))))
           for community in communities]
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
         use_community_layout=True, pos=None, k=None, node_size=500,
         font_size=12, legend_size='x-large', cdf=0.75, legend=True):
    colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple',
              'tab:brown', 'tab:pink', 'tab:olive', 'tab:cyan',
              'lawngreen', 'deepskyblue', 'lightsalmon', 'gold', 'black',
              'fuchsia', 'darkgoldenrod', 'teal']

    patches = list()

    if communities is None:
        communities = [nx_graph.nodes]  # a single community with all nodes

    # establish the layout of the nodes
    if pos is None:
        pos = nx.spring_layout(keep_only_communities(nx_graph, communities)
                               if use_community_layout else nx_graph, k=k)

    # for each community
    for i, comm in enumerate(communities):
        # draw the nodes of the community
        nx.draw_networkx_nodes(
            nx_graph, pos,
            nodelist=list(filter(nx_graph.nodes.__contains__, comm)),
            # node_color=f'C{i}',  # in a different colour
            node_color=colors[i % len(colors)],  # in a different colour
            node_size=node_size,
            alpha=0.8)

        # draw the edges of the community
        nx.draw_networkx_edges(
            nx_graph, pos,
            edgelist=get_community_graph(nx_graph, comm).edges,
            edge_color=colors[i % len(colors)],)

        # add a legend
        patches.append(mpatches.Patch(color=colors[i % len(colors)],
                                      label=get_community_label(comm,
                                                                cdf=cdf)))

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
        font_size=font_size,
        font_family=FONT)

    if len(patches) > 1 and legend:
        plt.legend(handles=patches, fontsize=legend_size)
    plt.show()
    return pos


# Assortativity


def get_assortativity(nx_graph):
    return nx.attribute_assortativity_coefficient(nx_graph, 'rime')


def shuffle(nx_graph):
    rimes = list(map(itemgetter('rime'),
                     map(itemgetter(1),
                         nx_graph.nodes(data=True))))
    random.shuffle(rimes)

    ret = nx_graph.copy()
    new_nodes = dict()
    for (node, attrs), rime in zip(ret.nodes(data=True), rimes):
        new_nodes[node] = attrs
        new_nodes[node]['rime'] = rime
    ret.update(nodes=new_nodes)
    return ret


def get_pval_sigma(nx_graph):
    n = 1000
    assort_seen = get_assortativity(nx_graph)
    assorts_gen = [get_assortativity(shuffle(nx_graph)) for _ in range(n)]

    pval = (1 + sum(map(assort_seen.__lt__, assorts_gen))) / (1 + n)

    assort_expected = statistics.mean(assorts_gen)
    assort_stdev = statistics.pstdev(assorts_gen, mu=assort_expected)
    sigma = (assort_seen - assort_expected) / assort_stdev

    return pval, sigma
