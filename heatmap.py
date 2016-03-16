import argparse, json, pickle, collections
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
from mapsim.simulation.sim import Sim

parser = argparse.ArgumentParser(description='Draws a graph.')
parser.add_argument('graph_file', help='the name of the graph file')
# parser.add_argument('trips', type=int, help='the name of the graph file')
# parser.add_argument('sim_length', type=int, help='the name of the graph file')
# parser.add_argument('bottlenecks', type=int, help='the name of the graph file')
parser.add_argument('--saveas', help='the name of the output file')

args = parser.parse_args()

config = {}
with open('config.json', 'r') as file:
    config = json.load(file)

config['graph_file'] = 'data/%s.graph' % args.graph_file

sim_data = {}
with open('data/' + args.graph_file + '.sim', 'rb') as file:
    sim_data = pickle.load(file)

sim = Sim(config, sim_data['segments'])
sim.setup()
history = sim.run()

edges = []
colors = []

for x, y, d in sim.graph.edges(data=True):

  if 'tts' in d:
    mean = np.mean(d['tts'])
    diff = mean - d['default_ttt']
    if mean > 0:
      edges.append((x, y))
      colors.append(diff)

positions = {}
for node in sim.graph.nodes(data = True):
    positions[node[0]] = (float(node[1]['lon']), float(node[1]['lat']))

#plt.figure(num=None, figsize=(16, 12), dpi=300, facecolor='w', edgecolor='k')
plt.figure(num=None, facecolor='w', edgecolor='k')
edge_plot = nx.draw_networkx_edges(
  sim.graph,
  pos=positions,
  edgelist=edges,
  edge_cmap=plt.get_cmap('jet'),
  edge_color=colors,
  width = 0.35,
  arrows = False)

plt.colorbar(edge_plot)
plt.axis('on')
plt.axes().set_aspect('equal', 'datalim')
plt.axes().set_axis_bgcolor('black')

# plt.show()
plt.savefig('test.pdf')





