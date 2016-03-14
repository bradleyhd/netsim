import networkx as nx
import argparse, json, random

from mapserver.graph.builder import GraphBuilder
from mapserver.graph.contractor import GraphContractor
from networkx.readwrite import json_graph
from mapserver.routing.router import Router

import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')

import matplotlib.pyplot as plt


parser = argparse.ArgumentParser(description='Constructs and contracts a graph.')
parser.add_argument('data_file', help='the name of the data file')
parser.add_argument('trips', help='number of routes to check')
parser.add_argument('--saveas', help='the name of the output file')

args = parser.parse_args()

config = {}
with open('config.json', 'r') as file:
    config = json.load(file)

data_file_path = 'data/%s.osm' % args.data_file

# build the graph
factory = GraphBuilder(config)
G = factory.from_file(data_file_path, True)
sim_data = factory.get_sim_data(True)

factory2 = GraphBuilder(config)
H = factory2.from_file(data_file_path)

# contract the graph
C = GraphContractor(config, G)
C.order_nodes()
C.contract_graph()
C.set_flags()

router = Router(G, decision_map=sim_data['decision_route_map'])

count = 0
check_path = []
path = []

for x in range(0, int(args.trips)):

    print(x)
    (start_node, end_node) = random.sample(list(G.nodes()), 2)
    #midgso
    # start_node = 23638
    # end_node = 23570

    try:
        check_path = nx.shortest_path(H,source = start_node,target = end_node, weight='ttt')
        check_path = list(zip(check_path, check_path[1:]))
    except:
        check_path = []

    path = router.route(start_node, end_node)

    if path != check_path:

        path_length = 0
        for x, y in path:
            path_length += G[x][y]['ttt']

        check_path_length = 0
        for x, y in check_path:
            check_path_length += H[x][y]['ttt']

        if path_length == check_path_length:
            continue

        count += 1
        print('Error, disagreement:')
        print('Contracted: %s' % path)
        print('NX: %s' % check_path)
        break

print('%d out of %s paths disagree' % (count, args.trips))

nodes = []
priorities = {}
colors = []
count = 0

plt.figure(num=None, figsize=(16, 12), dpi=300, facecolor='w', edgecolor='k')

positions = {}
for node in H.nodes(data = True):
    positions[node[0]] = (float(node[1]['lon']), float(node[1]['lat']))

labels = {}
h_labels = {}
# for n, d in H.nodes(data=True):
#     labels[n] = n
# for x, y, data in H.edges(data = True):
#     # if (x, y) in path or (x, y) in check_path:
#     labels[(x, y)] = data['ttt']

for x, y, data in G.edges(data = True):
    labels[(x, y)] = data['ttt']

for x, y, data in H.edges(data = True):
    h_labels[(x, y)] = data['ttt']

# for n, d in graph.nodes(data = True):
#   if 'decision_node' in d:
#     decision_nodes.append(n)

nx.draw_networkx_nodes(G, pos = positions, nodelist = G.nodes(), node_color = 'c', linewidths = 0, node_size = 0.05, node_shape = 'o')
edge_plot = nx.draw_networkx_edges(H, pos = positions, edgelist = H.edges(), edge_color = 'w', width = 0.05, alpha = 1.0, arrows = True)
edge_plot = nx.draw_networkx_edges(H, pos = positions, edgelist = [(x, y) for x, y, d in G.edges(data=True) if not d['is_shortcut']], edge_color = 'y', width = 0.05, alpha = 1.0, arrows = True)
# edge_plot = nx.draw_networkx_edges(H, pos = positions, edgelist = [(x, y) for x, y in G.edges() if 'up' in G[x][y]], edge_color = 'r', width = 0.05, alpha = 0.5, arrows = True)
# edge_plot = nx.draw_networkx_edges(H, pos = positions, edgelist = [(x, y) for x, y in G.edges() if 'down' in G[x][y]], edge_color = 'b', width = 0.05, alpha = 0.5, arrows = True)

edge_plot = nx.draw_networkx_edges(H, pos = positions, edgelist = path, edge_color = 'c', width = 0.05, alpha = 0.75, arrows = True)
edge_plot = nx.draw_networkx_edges(H, pos = positions, edgelist = check_path, edge_color = 'g', width = 0.05, alpha = 0.75, arrows = True)
props = dict(facecolor='none',edgecolor='none',boxstyle='round')
# nx.draw_networkx_edge_labels(G, pos=positions, edge_labels = labels, font_size=0.25, font_color='w', bbox=props)
# nx.draw_networkx_edge_labels(H, pos=positions, edge_labels = h_labels, font_size=0.25, font_color='w', bbox=props)


plt.axis('on')
plt.axes().set_aspect('equal', 'datalim')
plt.axes().set_axis_bgcolor('black')

plt.savefig('test.pdf')
