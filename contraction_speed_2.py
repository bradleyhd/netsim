import argparse, json, pickle, time
import os.path
import networkx as nx

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
  'greensboro'
]

times = []
shortcuts = []

for f in files:

  data_file_path = 'data/%s.osm' % f

  # build the graph
  factory = GraphBuilder(config)
  graph = factory.from_file(data_file_path, True)

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

  shortcuts.append(edge_delta)
  times.append(end)

print(times)
print(shortcuts)