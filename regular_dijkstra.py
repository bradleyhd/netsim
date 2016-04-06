import argparse, json, pickle, random
import os.path
import networkx as nx

from mapserver.graph.builder import GraphBuilder
from mapserver.graph.contractor2 import GraphContractor
from mapserver.routing.routerb import Router
from networkx.readwrite import json_graph

import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description='Constructs and contracts a graph.')
parser.add_argument('data_file', help='the name of the data file')
parser.add_argument('--saveas', help='the name of the output file')

args = parser.parse_args()

config = {}
with open('config.json', 'r') as file:
    config = json.load(file)

config = {}
with open('config.json', 'r') as file:
    config = json.load(file)

data_file_path = os.path.dirname(os.path.realpath(__file__)) + '/data/' + args.data_file + '.osm'

# build the graph
factory = GraphBuilder(config)
graph = factory.from_file(data_file_path, False)

r = Router(graph)
(start_node, end_node) = random.sample(list(graph.nodes()), 2)
start_node = 52942
end_node = 73496
route = r.route(start_node, end_node)
print(route)


nodes = []
priorities = {}
colors = []
count = 0

plt.figure(num=None, figsize=(18, 24), dpi=300, facecolor='k', edgecolor='k')

positions = {}
for node in graph.nodes(data = True):
    positions[node[0]] = (float(node[1]['lon']), float(node[1]['lat']))

reg_edges = []
touch_edges = []
for x, y, data in graph.edges(data = True):

    if 'touched' in data:
      touch_edges.append((x, y))
    elif not data['is_shortcut']:
      reg_edges.append((x, y))

    
labels = {}
for n, d in graph.nodes(data=True):
  labels[n] = n

props = dict(facecolor='none',edgecolor='none',boxstyle='round')

blue = '#5738FF'
purple = '#E747E7'
orange = '#E7A725'
green = '#A1FF47'
red = '#FF1E43'
gray = '#333333'
white = 'w'

nx.draw_networkx_nodes(graph, pos = positions, nodelist = [start_node], node_color = white, linewidths = 0, node_size = 40.0, node_shape = 'o')
nx.draw_networkx_nodes(graph, pos = positions, nodelist = [end_node], node_color = white, linewidths = 0, node_size = 40.0, node_shape = 's')

edge_plot = nx.draw_networkx_edges(graph, pos = positions, edgelist = reg_edges, edge_color = gray, width = 1.0, alpha = 1.0, arrows = False)
edge_plot = nx.draw_networkx_edges(graph, pos = positions, edgelist = touch_edges, edge_color = blue, width = 1.0, alpha = 1.0, arrows = False)
edge_plot = nx.draw_networkx_edges(graph, pos = positions, edgelist = route, edge_color = white, width = 1.0, alpha = 1.0, arrows = False)

# edge_plot = nx.draw_networkx_edges(graph, pos = positions, edgelist = down_edges, edge_color = 'b', width = 0.05, alpha = 1.0, arrows = False)
#nx.draw_networkx_labels(decision_graph, pos=positions, labels = labels, font_size=0.25, font_color='w', bbox=props)

plt.axis('off')
plt.axes().set_aspect('equal')
plt.axes().set_axis_bgcolor('black')

# plt.axes().set_xlim([-122.5081, -122.4033])
# # bottom, top
# plt.axes().set_ylim([37.7233, 37.7844])

plt.savefig('test.png', transparent=True)