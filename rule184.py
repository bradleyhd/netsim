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

    # "num_cars": 1000,
    # "cars_per_min": 100,
    # "sim_duration": 500,
    # "num_bottlenecks": 20,
    # "bottleneck_factor": 30,

    # "realtime": false,
    # "realtime_factor": 10,

    # "use_decision_graph": true,
    # "use_fast_contract": true,
    # "enable_lazy_updates": true,
    # "lazy_update_interval_fraction": 0.0000625,
    # "enable_hop_limit": true,
    # "hop_limit": 5,
    # "search_limit_fraction": 0.0000625,
    # "adaptive_routing": false,
    # "adaptive_routing_updates_s": 15,
    # "graph_weight_label": "ttt",
    # "graph_weight_smoothing_factor": 0.5,
    # "graph_weight_decay_factor": 0.9,

    # "routing_server_url": "http://localhost:5000",

    # "enable_location_history": false,
    # "location_history_poll_s": 1,

    # "cell_length_m": 5,
    # "speed_stdev_m/s": 5,
    # "acceleration_m/s^2": 2.8,
    # "acceleration_stdev_m/s^2": 0.5,
    # "driver_reaction_time_s": 0.2,
    

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

    road = []

    for (x, y) in [(1987, 1988), (1988, 1989), (1989, 322), (322, 1990), (1990, 1991), (1991, 1992), (1992, 397), (397, 1929), (1929, 1993)]: #, (1993, 1994), (1994, 5759), (5759, 5777), (5777, 5780), (5780, 5781), (5781, 1647), (1647, 1995), (1995, 5745), (5745, 5748), (5748, 1039), (1039, 1996), (1996, 1997), (1997, 1998), (1998, 5840), (5840, 693), (693, 1999), (1999, 792), (792, 2000), (2000, 2001), (2001, 5751), (5751, 5758), (5758, 2002), (2002, 2003), (2003, 2004), (2004, 2005), (2005, 5933), (5933, 2006), (2006, 2007), (2007, 2008), (2008, 2009), (2009, 2010), (2010, 2011), (2011, 2012)]:

      road.extend(sim.buckets[x][y]['buckets'].copy())

    logs.append(road.copy())

    yield sim.env.timeout(1)


def run(config):

  routes = []
  for id in range(config['num_cars']):
    routes.append(server.route(1987, 2012))

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
        xs.append(t)
        ys.append(p)

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
  ax.set_yticklabels([])
  plt.title('Nagel–Schreckenberg Flow Model', color=white)

  plt.scatter(xs, ys, color=blue, marker='.', s=1)

  plt.xlabel('Time (s)')
  plt.ylabel('Distance Travelled')
  plt.axes().set_axis_bgcolor('black')
  plt.axes().set_aspect('equal')

  ax.xaxis.label.set_color(white)
  ax.yaxis.label.set_color(white)
  ax.tick_params(axis='x', colors=white)
  ax.tick_params(axis='y', colors=white)
  ax.spines['bottom'].set_color(white)
  ax.spines['top'].set_color(white)
  ax.spines['left'].set_color(white)
  ax.spines['right'].set_color(white)

  plt.axes().set_ylim([0, max(ys) + 1])
  plt.axes().set_xlim([0, max(xs) + 1])
  plt.savefig('flow.png', transparent=True)
  # plt.show()

if __name__ == '__main__':

  run(config)
