import argparse, json, pickle, time
import os.path
import networkx as nx
import numpy as np

from mapserver.graph.builder import GraphBuilder
from mapserver.graph.contractor import GraphContractor
from networkx.readwrite import json_graph

import matplotlib.pyplot as plt

config = {}
with open('config.json', 'r') as file:
    config = json.load(file)

files = [
  'natchez',
  'battleground',
  'north_gso',
  'mid_gso',
  'greensboro',
  'guilford',
]

def successors(graph, x):

  x_pri = graph.node[x]['priority']
  return [y for y in iter(graph.succ[x].keys()) if graph.node[y]['priority'] > x_pri]

degree = []

data = [[]] * 2 * len(files)
count = 0

number_of_nodes = [[], []]
mean_degree = [[], []]
edges_added = [[], []]
times = [[], []]

for f in files:

  data_file_path = 'data/%s.osm' % f

  config['use_fast_contract'] = False

  # build the graph
  factory = GraphBuilder(config)
  graph = factory.from_file(data_file_path, False)
  graph2 = graph.copy()

  numed = graph.number_of_edges()

  # contract the graph
  C = GraphContractor(config, graph)

  start = time.perf_counter()
  C.order_nodes()
  C.contract_graph()
  C.set_flags()
  end = time.perf_counter() - start

  edges = C.G.number_of_edges()
  edge_delta = edges-numed

  number_of_nodes[0].append(graph.number_of_nodes())
  mean_degree[0].append(np.mean([len(successors(graph, n)) for n in graph.nodes()]))
  edges_added[0].append(edge_delta)
  times[0].append(end)

  count += 1

  config['use_fast_contract'] = True

  numed = graph2.number_of_edges()

  # contract the graph
  C = GraphContractor(config, graph2)

  start = time.perf_counter()
  C.order_nodes()
  C.contract_graph()
  C.set_flags()
  end = time.perf_counter() - start

  edges = C.G.number_of_edges()
  edge_delta = edges-numed

  number_of_nodes[1].append(graph2.number_of_nodes())
  mean_degree[1].append(np.mean([len(successors(graph2, n)) for n in graph2.nodes()]))
  edges_added[1].append(edge_delta)
  times[1].append(end)

  count += 1

  print(number_of_nodes)
  print(mean_degree)
  print(edges_added)
  print(times)

  print('---')

print(number_of_nodes)
print(mean_degree)
print(edges_added)
print(times)