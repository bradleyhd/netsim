import argparse, json, random, requests, os, logging
import matplotlib.pyplot as plt

from mapserver.routing.server import Server
from networkx.readwrite import json_graph as imports

parser = argparse.ArgumentParser(description='Draws a graph.')
parser.add_argument('graph_file', help='the name of the graph file')
parser.add_argument('--saveas', help='the name of the output file')

args = parser.parse_args()

config = {}
graph = None

with open('config.json', 'r') as file:
    config = json.load(file)

with open('data/' + args.graph_file + '.graph', 'r') as file:
      
    data = json.load(file)
    graph = imports.node_link_graph(data)

server = Server(config)
server._log.setLevel(logging.INFO)

num_edges = 0
for x, y, e in graph.edges(data=True):
  if 'real_arc' in e:
    num_edges += 1

for i in range(1, num_edges, 1000):

  print('Trying %.2f%%:' % ((i / num_edges) * 100))

  for j in range(0, i):

    x, y = random.choice(graph.edges())
    #duration = random.randint(100, graph[x][y]['ttt'] * 10)
    duration = graph[x][y]['ttt']
    server.report(x, y, duration, i)


stats = server._stats_data

# write stats to file
out_file_name = args.saveas + '.stats' if args.saveas else args.graph_file + '.stats'
out_file_path = os.path.dirname(os.path.realpath(__file__)) + '/data/' + out_file_name

f = open(out_file_path, 'w')
f.write(json.dumps(stats))
f.close()


# plot
plt.figure(num=None, figsize=(16, 12), dpi=300, facecolor='w', edgecolor='k')
xs = []
ys = []
for n, t in stats['repairs']:
  xs.append((n/num_edges)*100)
  ys.append(t)

plt.title('Repair Time by Percentage of Graph in Update')
plt.xlabel('% Edges Updated')
plt.ylabel('Repair Time (s)')
plt.plot(xs, ys)
plt.savefig('test.pdf')
