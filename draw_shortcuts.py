import argparse, json, pickle
import os.path
import networkx as nx

from mapserver.graph.builder import GraphBuilder
from mapserver.graph.contractor2 import GraphContractor
from networkx.readwrite import json_graph

import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description='Constructs and contracts a graph.')
parser.add_argument('data_file', help='the name of the data file')
parser.add_argument('--saveas', help='the name of the output file')

args = parser.parse_args()

config = {}
with open('config.json', 'r') as file:
    config = json.load(file)

data_file_path = os.path.dirname(os.path.realpath(__file__)) + '/data/' + args.data_file + '.osm'

# build the graph
factory = GraphBuilder(config)
graph, decision_graph = factory.from_file(data_file_path, True)

# decision_graph = graph.copy()

# contract the decision graph
C = GraphContractor(config, graph)
C.order_nodes()
C.contract_graph()
C.set_flags()

# # write regular graph to file
# out_file_name = args.saveas + '.graph' if args.saveas else args.data_file + '.graph'
# out_file_path = 'data/' + out_file_name
# f = open(out_file_path, 'w')
# data = json_graph.node_link_data(graph)
# f.write(json.dumps(data))
# f.close()

# # write decision graph to file
# out_file_name = args.saveas + '.decision.graph' if args.saveas else args.data_file + '.decision.graph'
# out_file_path = os.path.dirname(os.path.realpath(__file__)) + '/data/' + out_file_name
# f = open(out_file_path, 'w')
# data = json_graph.node_link_data(decision_graph)
# f.write(json.dumps(data))
# f.close()

# # write sim data to file
# out_file_name = args.saveas + '.sim' if args.saveas else args.data_file + '.sim'
# out_file_path = os.path.dirname(os.path.realpath(__file__)) + '/data/' + out_file_name
# f = open(out_file_path, 'wb')
# f.write(pickle.dumps(sim_data))
# f.close()

nodes = []
priorities = {}
colors = []
count = 0

plt.figure(num=None, figsize=(18, 24), dpi=300, facecolor='k', edgecolor='k')

positions = {}
for node in graph.nodes(data = True):
    positions[node[0]] = (float(node[1]['lon']), float(node[1]['lat']))

reg_edges = []
shortcuts = []
for x, y, data in graph.edges(data = True):
    if not data['is_shortcut']:
      reg_edges.append((x, y))
    else:
      shortcuts.append((x, y))

blue = '#5738FF'
purple = '#E747E7'
orange = '#E7A725'
green = '#A1FF47'
red = '#FF1E43'
gray = '#333333'
white = 'w'

# nx.draw_networkx_nodes(graph, pos = positions, nodelist = [start_node], node_color = magenta, linewidths = 0, node_size = 40.0, node_shape = '>')
# nx.draw_networkx_nodes(graph, pos = positions, nodelist = [end_node], node_color = magenta, linewidths = 0, node_size = 40.0, node_shape = 's')

edge_plot = nx.draw_networkx_edges(graph, pos = positions, edgelist = reg_edges, edge_color = white, width = 1.0, alpha = 1.0, arrows = False)
edge_plot = nx.draw_networkx_edges(graph, pos = positions, edgelist = shortcuts, edge_color = red, width = 0.5, alpha = 0.7, arrows = False)
# edge_plot = nx.draw_networkx_edges(graph, pos = positions, edgelist = route, edge_color = magenta, width = 1.0, alpha = 1.0, arrows = False)

plt.axis('off')
plt.axes().set_aspect('equal')
plt.axes().set_axis_bgcolor('black')

# plt.axes().set_xlim([-122.4400, -122.3875])
# # bottom, top
# plt.axes().set_ylim([37.7600, 37.8000])

plt.savefig('test.png', transparent=True)
