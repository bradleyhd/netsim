import argparse, json, logging, random, datetime, os.path, pickle, copy, requests
import networkx as nx
import time as time
import matplotlib.pyplot as plt
import numpy as np
from mapserver.routing.server import Server
from matplotlib import colors

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
    logs.append(road.copy())

    yield sim.env.timeout(1)


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

  xs = []
  ys = []

  for t in range(len(logs)):
    for p in range(len(logs[t])):
      if logs[t][p] > 0:
        ys.append(p)
        xs.append(t)

  import matplotlib.pyplot as plt
  import matplotlib.image as mpimg
  import numpy as np

  blue = '#5738FF'
  purple = '#E747E7'
  orange = '#E7A725'
  green = '#A1FF47'
  red = '#FF1E43'
  gray = '#333333'
  white = 'w'

  fig = plt.figure(num=None, figsize=(12, 8), dpi=300, facecolor='k', edgecolor='k')
  ax = fig.gca()
  plt.title('Nagel–Schreckenberg Flow Model', color=white)

  plt.scatter(xs, ys, color='b', marker='o', s=5)

  plt.xlabel('Time (s)')
  plt.ylabel('Distance From Start of Road Segment')
  plt.axes().set_axis_bgcolor('black')

  ax.xaxis.label.set_color(white)
  ax.yaxis.label.set_color(white)
  ax.tick_params(axis='x', colors=white)
  ax.tick_params(axis='y', colors=white)
  ax.spines['bottom'].set_color(white)
  ax.spines['top'].set_color(white)
  ax.spines['left'].set_color(white)
  ax.spines['right'].set_color(white)

  plt.axes().set_xlim([0, max(xs) + 1])
  plt.axes().set_ylim([0, max(ys) + 1])
  plt.savefig('flow.png', transparent=True)
  # plt.show()

if __name__ == '__main__':

  run(config)
