import networkx as nx
import numpy as np
import argparse, json, random, time

from mapserver.graph.builder import GraphBuilder
from mapserver.graph.contractor import GraphContractor
from networkx.readwrite import json_graph
from mapserver.routing.router import Router
from mapserver.util.timer import Timer

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

# with open('data/battleground_merged.graph', 'r') as file:
      
#       data = json.load(file)
#       G = json_graph.node_link_graph(data)
sim_data = factory.get_sim_data(True)

factory2 = GraphBuilder(config)
H = factory2.from_file(data_file_path)

# contract the graph
C = GraphContractor(config, G)
C.order_nodes()
C.contract_graph()
C.set_flags()

#decision_map=sim_data['decision_route_map']
router = Router(G, decision_map=sim_data['decision_route_map'])

broken = []
for (x, y), path in sim_data['decision_route_map'].items():

    length = 0
    for (u, v) in path:
        length += H[u][v]['ttt']

    if x in G and y in G[x]:
        if length != G[x][y]['ttt']:
            broken.append((x, y))
            print('path: %s scut %s' % (length, G[x][y]['ttt']))
            print(path)

count = 0
check_path = []
path = []

ref_speeds = []
imp_speeds = []

for x in range(0, int(args.trips)):

    (start_node, end_node) = random.sample(list(G.nodes()), 2)

    #midgso
    # start_node = 23638
    # end_node = 23570

    #northgso
    # start_node = 6283
    # end_node = 6616

    # start_node = '2862739088'
    # end_node = '2862739078'

    # start_node = 208
    # end_node = 132

    print('%s: %s->%s' % (x, start_node, end_node))

    start_1 = time.perf_counter()
    try:
        check_path = nx.shortest_path(H,source = start_node,target = end_node, weight='ttt')
        check_path = list(zip(check_path, check_path[1:]))
    except:
        check_path = []
    end_1 = time.perf_counter() - start_1
    ref_speeds.append(end_1)

    start_2 = time.perf_counter()
    path = router.route(start_node, end_node)
    end_2 = time.perf_counter() - start_2
    imp_speeds.append(end_2)

    print('Speed difference: %s' % (end_1 - end_2))

    if path != check_path:

        # chunk = []
        # for x in range(len(check_path)):
        #     if check_path[x] not in path:
        #         chunk.append(check_path[x])

        # if chunk:
        #     print(chunk)
        #     print(sim_data['decision_route_map'][chunk[0][0], chunk[-1][1]])


        path_length = 0
        for x, y in path:
            path_length += H[x][y]['ttt']

        check_path_length = 0
        for x, y in check_path:
            check_path_length += H[x][y]['ttt']

        print('path length: %s' % path_length)
        print('check length: %s' % check_path_length)

        if path_length == check_path_length:
            continue

        count += 1
        print('Error, disagreement:')
        print('Contracted:\n%s' % path)
        print('NX:\n%s' % check_path)
        break

print('%d out of %s paths disagree' % (count, args.trips))

print('Ref: Mean: %s' % np.mean(ref_speeds))
print('Imp: Mean: %s' % np.mean(imp_speeds))
print('Ref: Median: %s' % np.median(ref_speeds))
print('Imp: Median: %s' % np.median(imp_speeds))
print('')
print('Mean speedup: %s' % (np.mean(ref_speeds)/np.mean(imp_speeds)))


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

for x, y, data in G.edges(data = True):
    # if (x, y) in path:
    if not data['is_shortcut']:
        labels[(x, y)] = data['ttt']

# for x, y, data in H.edges(data = True):
#     if (x, y) in check_path:
#         h_labels[(x, y)] = data['ttt']

# for n, d in graph.nodes(data = True):
#   if 'decision_node' in d:
#     decision_nodes.append(n)

nx.draw_networkx_nodes(G, pos = positions, nodelist = G.nodes(), node_color = 'c', linewidths = 0, node_size = 0.05, node_shape = 'o')
edge_plot = nx.draw_networkx_edges(H, pos = positions, edgelist = H.edges(), edge_color = 'w', width = 0.05, alpha = 1.0, arrows = True)
edge_plot = nx.draw_networkx_edges(H, pos = positions, edgelist = [(x, y) for x, y, d in G.edges(data=True) if not d['is_shortcut']], edge_color = 'y', width = 0.05, alpha = 1.0, arrows = True)
# edge_plot = nx.draw_networkx_edges(H, pos = positions, edgelist = [(x, y) for x, y in G.edges() if 'up' in G[x][y]], edge_color = 'r', width = 0.05, alpha = 0.5, arrows = True)
# edge_plot = nx.draw_networkx_edges(H, pos = positions, edgelist = [(x, y) for x, y in G.edges() if 'down' in G[x][y]], edge_color = 'b', width = 0.05, alpha = 0.5, arrows = True)

edge_plot = nx.draw_networkx_edges(H, pos = positions, edgelist = path, edge_color = 'r', width = 0.05, alpha = 1.0, arrows = True)
edge_plot = nx.draw_networkx_edges(H, pos = positions, edgelist = check_path, edge_color = 'g', width = 0.05, alpha = 1.0, arrows = True)
#edge_plot = nx.draw_networkx_edges(H, pos = positions, edgelist = broken, edge_color = 'b', width = 0.05, alpha = 1.0, arrows = True)


props = dict(facecolor='none',edgecolor='none',boxstyle='round')
nx.draw_networkx_edge_labels(G, pos=positions, edge_labels = labels, font_size=0.25, font_color='w', bbox=props)
nx.draw_networkx_edge_labels(H, pos=positions, edge_labels = h_labels, font_size=0.25, font_color='w', bbox=props)
# nx.draw_networkx_labels(H, pos=positions, labels = labels, font_size=0.25, font_color='w', bbox=props)


plt.axis('on')
plt.axes().set_aspect('equal', 'datalim')
plt.axes().set_axis_bgcolor('black')

plt.savefig('test.pdf')
