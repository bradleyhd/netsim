import argparse, json, pickle
import os.path
import networkx as nx

from mapserver.graph.builder import GraphBuilder
from mapserver.graph.contractor import GraphContractor
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
sim_data = factory.get_sim_data()

# contract the decision graph
C = GraphContractor(config, decision_graph)
C.order_nodes()
C.contract_graph()
C.set_flags()

# write regular graph to file
out_file_name = args.saveas + '.graph' if args.saveas else args.data_file + '.graph'
out_file_path = 'data/' + out_file_name
f = open(out_file_path, 'w')
data = json_graph.node_link_data(graph)
f.write(json.dumps(data))
f.close()

# write decision graph to file
out_file_name = args.saveas + '.decision.graph' if args.saveas else args.data_file + '.decision.graph'
out_file_path = os.path.dirname(os.path.realpath(__file__)) + '/data/' + out_file_name
f = open(out_file_path, 'w')
data = json_graph.node_link_data(decision_graph)
f.write(json.dumps(data))
f.close()

# write sim data to file
out_file_name = args.saveas + '.sim' if args.saveas else args.data_file + '.sim'
out_file_path = os.path.dirname(os.path.realpath(__file__)) + '/data/' + out_file_name
f = open(out_file_path, 'wb')
f.write(pickle.dumps(sim_data))
f.close()

# nodes = []
# priorities = {}
# colors = []
# count = 0

# plt.figure(num=None, figsize=(16, 12), dpi=300, facecolor='w', edgecolor='k')

# positions = {}
# for node in graph.nodes(data = True):
#     #print(node)
#     positions[node[0]] = (float(node[1]['lon']), float(node[1]['lat']))

# reg_edges = []
# up_edges = []
# down_edges = []
# for x, y, data in graph.edges(data = True):
#     if not 'dc' in data:
#       reg_edges.append((x, y))
#     else:
#       up_edges.append((x, y))
#     # if 'up' in data:
#     #     up_edges.append((x, y))
#     # if 'down' in data:
#     #     down_edges.append((x, y))

# # for n, d in graph.nodes(data = True):
# #   if 'decision_node' in d:
# #     decision_nodes.append(n)

# nx.draw_networkx_nodes(graph, pos = positions, nodelist = graph.nodes(), node_color = 'c', linewidths = 0, node_size = 1.0, node_shape = 'o')
# edge_plot = nx.draw_networkx_edges(graph, pos = positions, edgelist = reg_edges, edge_color = 'w', width = 0.05, alpha = 1.0, arrows = True)

# edge_plot = nx.draw_networkx_edges(graph, pos = positions, edgelist = up_edges, edge_color = 'r', width = 0.05, alpha = 1.0, arrows = True)
# # edge_plot = nx.draw_networkx_edges(graph, pos = positions, edgelist = down_edges, edge_color = 'b', width = 0.05, alpha = 1.0, arrows = False)


# plt.axis('on')
# plt.axes().set_aspect('equal', 'datalim')
# plt.axes().set_axis_bgcolor('black')

# plt.savefig('test.pdf')
