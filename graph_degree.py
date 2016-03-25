import argparse, json, pickle, time, random
import os.path
import networkx as nx
import numpy as np

from mapserver.graph.builder import GraphBuilder
from mapserver.graph.contractor2 import GraphContractor
from mapserver.routing.router2 import Router
from networkx.readwrite import json_graph

import matplotlib.pyplot as plt

config = {}
with open('config.json', 'r') as file:
    config = json.load(file)

files = [
  # 'natchez',
  # 'battleground',
  # 'north_gso',
  # 'mid_gso',
  # 'greensboro',
  # 'guilford',
  # 'charlotte',
  'nc',
]

def successors(graph, x):

  x_pri = graph.node[x]['priority']
  return [y for y in iter(graph.succ[x].keys()) if graph.node[y]['priority'] > x_pri]

degree = []

count = 0
trips = 1000

number_of_nodes = [[], []]
mean_degree = [[], []]
edges_added = [[], []]
contract_times = [[], []]
route_times = [[], []]

for f in files:

  data_file_path = 'data/%s.osm' % f

  config['use_fast_contract'] = False

  # build the graph
  factory = GraphBuilder(config)
  graph = factory.from_file(data_file_path, False)

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
  contract_times[0].append(end)

  router = Router(graph)
  times = []
  coords = []

  for x in range(0, trips):

    (start_node, end_node) = random.sample(list(graph.nodes()), 2)
    start = time.perf_counter()
    router.route(start_node, end_node)
    end = time.perf_counter() - start
    coords.append((start_node, end_node))
    times.append(end)

  route_times[0].append(np.median(times))

  count += 1

  config['use_fast_contract'] = True

  # build the graph
  factory = GraphBuilder(config)
  graph2 = factory.from_file(data_file_path, False)

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
  contract_times[1].append(end)

  router = Router(graph2)
  times = []

  for x in range(0, trips):

    (start_node, end_node) = coords[x]
    start = time.perf_counter()
    router.route(start_node, end_node)
    end = time.perf_counter() - start
    times.append(end)

  route_times[1].append(np.median(times))

  count += 1

  print('Nodes: %s' % number_of_nodes)
  print('Mean Outdegree: %s' % mean_degree)
  print('Shortcuts Added: %s' % edges_added)
  print('Contraction Times: %s' % contract_times)
  print('Route Times: %s' % route_times)

  print('---')

print('Nodes: %s' % number_of_nodes)
print('Mean Outdegree: %s' % mean_degree)
print('Shortcuts Added: %s' % edges_added)
print('Contraction Times: %s' % contract_times)
print('Route Times: %s' % route_times)