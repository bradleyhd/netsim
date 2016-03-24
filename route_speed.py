import argparse, json, pickle, time, random
import os.path
import networkx as nx
import numpy as np

from mapserver.graph.builder import GraphBuilder
from mapserver.graph.contractor import GraphContractor
from networkx.readwrite import json_graph
from mapserver.routing.router import Router

import matplotlib.pyplot as plt

config = {}
with open('config.json', 'r') as file:
    config = json.load(file)

files = [
  # 'natchez',
  'battleground',
  # 'north_gso',
  # 'mid_gso',
  # 'greensboro',
  # 'guilford',
]

count = 0
trips = 1

number_of_nodes = [[], []]
route_times = [[], []]

for f in files:

  data_file_path = 'data/%s.osm' % f

  config['use_fast_contract'] = True

  # build the graph
  factory = GraphBuilder(config)
  graph = factory.from_file(data_file_path, False)
  graph2 = graph.copy()

  # contract the graph
  C = GraphContractor(config, graph)

  C.order_nodes()
  C.contract_graph()
  C.set_flags()

  # route
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

  number_of_nodes[0].append(graph.number_of_nodes())
  route_times[0].append(np.median(times))

  count += 1

  #--------

  # config['use_fast_contract'] = True

  # # contract the graph
  # C = GraphContractor(config, graph2)

  # C.order_nodes()
  # C.contract_graph()
  # C.set_flags()

  # # route
  # router = Router(graph2)

  # times = []

  # for x in range(0, trips):

  #   (start_node, end_node) = coords[x]
  #   start = time.perf_counter()
  #   router.route(start_node, end_node)
  #   end = time.perf_counter() - start
  #   times.append(end)

  # number_of_nodes[1].append(graph2.number_of_nodes())
  # route_times[1].append(np.median(times))

  # count += 1


  print(number_of_nodes)
  print(route_times)

  print('---')

print(number_of_nodes)
print(route_times)
