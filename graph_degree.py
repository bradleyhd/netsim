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
  'natchez',
  'battleground',
  'north_gso',
  'mid_gso',
  'greensboro',
  'guilford',
  # 'charlotte',
  # 'nc',
]

def successors(graph, x):

  x_pri = graph.node[x]['priority']
  return [y for y in iter(graph.succ[x].keys()) if graph.node[y]['priority'] > x_pri]

degree = []

count = 0
trips = 5000

number_of_nodes = [[], [], [], []]
mean_degree = [[], [], [], []]
edges_added = [[], [], [], []]
contract_times = [[], [], [], []]
route_times = [[], [], [], []]
repair_times = [[], [], [], []]

for f in files:

  data_file_path = 'data/%s.osm' % f

  # ------
  # EDS5 regular
  # ------

  config['use_fast_contract'] = False
  config['use_decision_graph'] = False

  # build the graph
  factory = GraphBuilder(config)
  graph = factory.from_file(data_file_path, config['use_decision_graph'])

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

  start = time.perf_counter()
  C.repair({})
  end = time.perf_counter() - start
  repair_times[0].append(end)

  count += 1

  # ------
  # D5 regular
  # ------  

  config['use_fast_contract'] = True
  config['use_decision_graph'] = False

  # build the graph
  factory = GraphBuilder(config)
  graph2 = factory.from_file(data_file_path, config['use_decision_graph'])
  sim_data = factory.get_sim_data()

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

  start = time.perf_counter()
  C.repair({})
  end = time.perf_counter() - start
  repair_times[1].append(end)

  count += 1

  # ------
  # EDS5 decision
  # ------

  config['use_fast_contract'] = False
  config['use_decision_graph'] = True

  # build the graph
  factory = GraphBuilder(config)
  ref_graph3, graph3 = factory.from_file(data_file_path, config['use_decision_graph'])
  sim_data = factory.get_sim_data()

  numed = graph3.number_of_edges()

  # contract the graph
  C = GraphContractor(config, graph3, decision_map=sim_data['decision_route_map'], reference_graph=ref_graph3)

  start = time.perf_counter()
  C.order_nodes()
  C.contract_graph()
  C.set_flags()
  end = time.perf_counter() - start

  edges = C.G.number_of_edges()
  edge_delta = edges-numed

  number_of_nodes[2].append(graph3.number_of_nodes())
  mean_degree[2].append(np.mean([len(successors(graph3, n)) for n in graph3.nodes()]))
  edges_added[2].append(edge_delta)
  contract_times[2].append(end)

  router = Router(graph3, decision_map=sim_data['decision_route_map'])
  times = []
  coords = []

  for x in range(0, trips):

    (start_node, end_node) = random.sample(list(graph3.nodes()), 2)
    start = time.perf_counter()
    router.route(start_node, end_node)
    end = time.perf_counter() - start
    coords.append((start_node, end_node))
    times.append(end)

  route_times[2].append(np.median(times))

  start = time.perf_counter()
  C.repair({})
  end = time.perf_counter() - start
  repair_times[2].append(end)

  count += 1

  # ------
  # D5 fast
  # ------  

  config['use_fast_contract'] = True
  config['use_decision_graph'] = True

  # build the graph
  factory = GraphBuilder(config)
  ref_graph4, graph4 = factory.from_file(data_file_path, config['use_decision_graph'])
  sim_data = factory.get_sim_data()

  numed = graph4.number_of_edges()

  # contract the graph
  C = GraphContractor(config, graph4, decision_map=sim_data['decision_route_map'], reference_graph=ref_graph4)

  start = time.perf_counter()
  C.order_nodes()
  C.contract_graph()
  C.set_flags()
  end = time.perf_counter() - start

  edges = C.G.number_of_edges()
  edge_delta = edges-numed

  number_of_nodes[3].append(graph4.number_of_nodes())
  mean_degree[3].append(np.mean([len(successors(graph4, n)) for n in graph4.nodes()]))
  edges_added[3].append(edge_delta)
  contract_times[3].append(end)

  router = Router(graph4, decision_map=sim_data['decision_route_map'])
  times = []

  for x in range(0, trips):

    (start_node, end_node) = coords[x]
    start = time.perf_counter()
    router.route(start_node, end_node)
    end = time.perf_counter() - start
    times.append(end)

  route_times[3].append(np.median(times))

  start = time.perf_counter()
  C.repair({})
  end = time.perf_counter() - start
  repair_times[3].append(end)

  count += 1

  print('Nodes: %s' % number_of_nodes)
  print('Mean Outdegree: %s' % mean_degree)
  print('Shortcuts Added: %s' % edges_added)
  print('Contraction Times: %s' % contract_times)
  print('Route Times: %s' % route_times)
  print('Repair Times: %s' % repair_times)

  print('---')

print('Nodes: %s' % number_of_nodes)
print('Mean Outdegree: %s' % mean_degree)
print('Shortcuts Added: %s' % edges_added)
print('Contraction Times: %s' % contract_times)
print('Repair Times: %s' % repair_times)
print('Route Times: %s' % route_times)