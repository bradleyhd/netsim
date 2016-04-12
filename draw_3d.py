import argparse, json, pickle
import os.path
import networkx as nx

from mapserver.graph.builder import GraphBuilder
from mapserver.graph.contractor2 import GraphContractor
from networkx.readwrite import json_graph
from mpl_toolkits.mplot3d import Axes3D

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
graph = factory.from_file(data_file_path, False)

# graph = graph.copy()

# contract the decision graph
C = GraphContractor(config, graph)
C.order_nodes()
C.contract_graph()
C.set_flags()

nodes = []
priorities = {}
colors = []
count = 0

fig = plt.figure(figsize=(12, 8), dpi=300)
#fig = plt.figure()
ax = fig.gca(projection='3d')

blue = '#5738FF'
purple = '#E747E7'
orange = '#E7A725'
green = '#A1FF47'
red = '#FF1E43'
gray = '#333333'
white = 'w'

for node_1, node_2, data in graph.edges(data = True):

        # if 'real_arc' in data:
        #     #continue

        x_1 = graph.node[node_1]['lon']
        y_1 = graph.node[node_1]['lat']
        x_2 = graph.node[node_2]['lon']
        y_2 = graph.node[node_2]['lat']
        z_1 = graph.node[node_1]['priority']
        z_2 = graph.node[node_2]['priority']
        # z_1 = 1
        # z_2 = 1

        # color = 'b'
        if data['is_shortcut'] == True:
            color = purple
        else:
          color = white

        ax.plot([x_1, x_2], [y_1, y_2], [z_1, z_2], color = color)

            # if data['highway'] in ['motorway', 'motorway_link', 'trunk', 'trunk_link', 'primary', 'primary_link']:
            #     z_1 = 10
            #     z_2 = 10
            #     color = 'g'

            # elif data['highway'] in ['secondary', 'secondary_link', 'tertiary', 'tertiary_link', 'road']:
            #     z_1 = 5
            #     z_2 = 5
            #     color = 'y'
            # else:
            #     z_1 = 0
            #     z_2 = 0
            #     color = 'r'

        # xs.extend([x_1, x_2])
        # ys.extend([y_1, y_2])
        # zs.extend([z_1, z_2])
        # colors.append(color)

        # ax.plot([x_1, x_2], [y_1, y_2], [z_1, z_2], color = color)

plt.axis('on')
ax.w_xaxis.set_pane_color((0.0, 0.0, 0.0, 1.0))
ax.w_yaxis.set_pane_color((0.0, 0.0, 0.0, 1.0))
ax.w_zaxis.set_pane_color((0.0, 0.0, 0.0, 1.0))
ax.w_xaxis._axinfo.update({'grid' : {'color': gray}})
ax.w_yaxis._axinfo.update({'grid' : {'color': gray}})
ax.w_zaxis._axinfo.update({'grid' : {'color': gray}})
ax.set_xticklabels([])
ax.set_yticklabels([])
ax.set_zticklabels([])
# plt.axes().set_aspect('equal')
# plt.axes().set_axis_bgcolor('black')

# plt.axes().set_xlim([-122.4193, -122.3931])
# # bottom, top
# plt.axes().set_ylim([37.7763, 37.7916])

#plt.show()
plt.savefig('test.png', transparent=True)
