import argparse, json, logging, random, datetime, os.path, pickle, requests
import networkx as nx
import time as time
import matplotlib.pyplot as plt
import numpy as np

from networkx.readwrite import json_graph
from mapsim.simulation.sim import Sim
from copy import deepcopy

parser = argparse.ArgumentParser(description='Draws a graph.')
parser.add_argument('graph_file', help='the name of the graph file')
parser.add_argument('--saveas', help='the name of the output file')

args = parser.parse_args()

smoothing_factors = [0.3, 0.5, 0.7, 0.9]
decay_factors = [1]
# smoothing_factors = [0.1]
# decay_factors = [0.9]
results = []

def run(sim, smoothing_factor, decay_factor, routes):

  sim._config['graph_weight_smoothing_factor'] = smoothing_factor
  sim._config['graph_weight_decay_factor'] = decay_factor

  # --
  # Run without adaptive routing
  # --

  sim._config['adaptive_routing'] = False

  res = requests.get('%s/restart/%s/%s' % (config['routing_server_url'], smoothing_factor, decay_factor))

  sim.setup()
  history1 = sim.run()
  cars1 = []
  for car in sim.cars:
    cars1.append({
      'id': car.id,
      'driving_time': car.total_driving_time,
      'done': car.done
    })

  # --
  # Run with adaptive routing
  # --

  sim._config['adaptive_routing'] = True

  res = requests.get('%s/restart/%s/%s' % (config['routing_server_url'], smoothing_factor, decay_factor))

  sim.setup()
  history2 = sim.run()
  cars2 = []
  for car in sim.cars:
    cars2.append({
      'id': car.id,
      'driving_time': car.total_driving_time,
      'done': car.done
    })

  # --
  # Calculate speedup
  # --

  xs = []
  ys = []
  for i in range(len(cars2)):
    if cars1[i]['done'] and cars2[i]['done']:
      speedup = (cars1[i]['driving_time'] - cars2[i]['driving_time'])
      xs.append(i);
      ys.append(speedup)

  print('Smoothing: %s Decay: %s' % (smoothing_factor, decay_factor))
  results.append((smoothing_factor, decay_factor, np.mean(ys)))
  try:
    print('Mean: %s Median: %s' % (np.mean(ys), np.median(ys)))
  except:
    pass

if __name__ == '__main__':

  config = {}
  with open('config.json', 'r') as file:
      config = json.load(file)

  config['graph_file'] = 'data/%s.graph' % args.graph_file

  sim_data = {}
  with open('data/' + args.graph_file + '.sim', 'rb') as file:
      sim_data = pickle.load(file)

  res = requests.get('http://localhost:5000/routes/generate/%d' % (config['num_cars']))
  routes = res.json()

  sim = Sim(config, sim_data['segments'], routes)
  
  for s in smoothing_factors:
    for d in decay_factors:
      run(sim, s, d, routes)

  f = open('results.txt', 'w')
  f.write(json.dumps(results))
  f.close()

