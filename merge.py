import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import json, argparse, os
from networkx.readwrite import json_graph
import networkx as nx
from mapserver.graph.contractor import GraphContractor

parser = argparse.ArgumentParser(description='Draws a graph in 3d.')
parser.add_argument('data_file', help='the name of the graph file')
parser.add_argument('--saveas', help='the name of the output file')

args = parser.parse_args()

config = {}
with open('config.json', 'r') as file:
    config = json.load(file)

with open('data/' + args.data_file + '_1.graph', 'r') as file:
      
    data = json.load(file)
    graph = json_graph.node_link_graph(data)

with open('data/' + args.data_file + '_2.graph', 'r') as file:
      
    data = json.load(file)
    graph_2 = json_graph.node_link_graph(data)

with open('data/' + args.data_file + '_3.graph', 'r') as file:
      
    data = json.load(file)
    graph_3 = json_graph.node_link_graph(data)

for n, d in graph.nodes(data=True):
  d['tier'] = 1

for n in graph_2.nodes():
  if not 'tier' in graph.node[n]:
    graph.node[n]['tier'] = 2

for n in graph_3.nodes():
  if not 'tier' in graph.node[n]:
    graph.node[n]['tier'] = 3

for x, y, d in graph_2.edges(data=True):
  graph.add_edge(x, y, **d)

for x, y, d in graph_3.edges(data=True):
  graph.add_edge(x, y, **d)

# C = GraphContractor(config, graph)
# C.set_flags()

for u, v, edge_data in graph.edges_iter(data = True):

    u_priority = graph.node[u]['priority']
    v_priority = graph.node[v]['priority']

    u_tier = graph.node[u]['tier']
    v_tier = graph.node[v]['tier']

    # for edge going from u -> v
    if u_priority < v_priority or u_tier > v_tier:
        edge_data['level'] = 1
        edge_data['up'] = True
    elif u_priority > v_priority or u_tier < v_tier:
        edge_data['level'] = -1
        edge_data['down'] = True
    else:
        print('wtf %s %s' % (u, v))

# write graph to file
out_file_name = args.saveas + '_merged.graph' if args.saveas else args.data_file + '_merged.graph'
out_file_path = os.path.dirname(os.path.realpath(__file__)) + '/data/' + out_file_name

f = open(out_file_path, 'w')
data = json_graph.node_link_data(graph)
f.write(json.dumps(data))
f.close()

# nodes = []
# priorities = {}
# colors = []
# count = 0

# plt.figure(num=None, figsize=(16, 12), dpi=300, facecolor='w', edgecolor='k')

# positions = {}
# for node in graph.nodes(data = True):
#     positions[node[0]] = (float(node[1]['lon']), float(node[1]['lat']))

# reg_edges = []
# up_edges = []
# down_edges = []
# for x, y, data in graph.edges(data = True):
#     if not data['is_shortcut']:
#         reg_edges.append((x, y))
#     if 'up' in data:
#         up_edges.append((x, y))
#     if 'down' in data:
#         down_edges.append((x, y))

# # for n, d in graph.nodes(data = True):
# #   if 'decision_node' in d:
# #     decision_nodes.append(n)

# #nx.draw_networkx_nodes(graph, pos = positions, nodelist = decision_nodes, node_color = 'c', linewidths = 0, node_size = 0.05, node_shape = 'o')
# edge_plot = nx.draw_networkx_edges(graph, pos = positions, edgelist = reg_edges, edge_color = 'w', width = 0.05, alpha = 1.0, arrows = False)

# edge_plot = nx.draw_networkx_edges(graph, pos = positions, edgelist = up_edges, edge_color = 'r', width = 0.05, alpha = 1.0, arrows = False)
# edge_plot = nx.draw_networkx_edges(graph, pos = positions, edgelist = down_edges, edge_color = 'b', width = 0.05, alpha = 1.0, arrows = False)


# plt.axis('on')
# plt.axes().set_aspect('equal', 'datalim')
# plt.axes().set_axis_bgcolor('black')

# plt.savefig('test.pdf')
