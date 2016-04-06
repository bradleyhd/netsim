import argparse, json, logging, random, datetime, os.path, pickle, copy, requests
import networkx as nx
import time as time
import matplotlib.pyplot as plt
import numpy as np
from mapserver.routing.server import Server

from networkx.readwrite import json_graph
from mapsim.simulation.sim2 import Sim
from copy import deepcopy

parser = argparse.ArgumentParser(description='Draws a graph.')
parser.add_argument('graph_file', help='the name of the graph file')
parser.add_argument('--saveas', help='the name of the output file')

args = parser.parse_args()

config = {}
with open('config.json', 'r') as file:
    config = json.load(file)

if config['use_decision_graph']:
  config['graph_file'] = 'data/%s.decision.graph' % args.graph_file
  config['sim_file'] = 'data/%s.sim' % args.graph_file
  config['reference_graph_file'] = 'data/%s.graph' % args.graph_file
else:
  config['graph_file'] = 'data/%s.graph' % args.graph_file

server = Server(config)

logs = []
def edge_watcher(sim):

  while True:

    road = sim.buckets[1997][1998]['buckets'].copy()
    road.extend(sim.buckets[1998][5840]['buckets'].copy())
    road.extend(sim.buckets[5840][693]['buckets'].copy())
    road.extend(sim.buckets[693][1999]['buckets'].copy())
    road.extend(sim.buckets[1999][792]['buckets'].copy())
    # print(road)
    logs.append(road.copy())

    yield sim.env.timeout(0.5)


def run(config):

  routes = []
  for id in range(config['num_cars']):
    routes.append(server.route(1039, 2005))

  config = copy.deepcopy(config)
  config['graph_file'] = 'data/%s.graph' % args.graph_file

  config['adaptive_routing'] = False
  sim = Sim(server, config, routes)
  sim.setup()
  sim.env.process(edge_watcher(sim))
  sim.run()

  import matplotlib.pyplot as plt
  import matplotlib.image as mpimg
  import numpy as np

  # for log in logs:
  #   print(log)


  # print(np.array(logs))
  # print(np.array(logs).shape)
  # plt.figure()
  # plt.imshow(np.array(logs), interpolation='nearest', aspect='auto', cmap="hot")
  # plt.matshow(logs)
  plt.matshow(logs, fignum=100, cmap=plt.cm.gray)
  # plt.axes().set_xlim([500, 1000])
  # plt.axes().set_aspect('equal')
  plt.show()

if __name__ == '__main__':

  run(config)
