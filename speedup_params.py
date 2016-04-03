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
# parser.add_argument('trips', type=int, help='the name of the graph file')
# parser.add_argument('sim_length', type=int, help='the name of the graph file')
# parser.add_argument('bottlenecks', type=int, help='the name of the graph file')
parser.add_argument('--saveas', help='the name of the output file')

args = parser.parse_args()

smoothing_factors = [0.1, 0.25, 0.5, 0.75, 0.9]
decay_factors = [0.1, 0.25, 0.5, 0.75, 0.9]
# smoothing_factors = [0.1]
# decay_factors = [0.5]
results = []

def run(sim, smoothing_factor, decay_factor):

  sim._config['graph_weight_smoothing_factor'] = smoothing_factor
  sim._config['graph_weight_decay_factor'] = decay_factor
  sim._config['adaptive_routing'] = False
  
  sim.setup()
  history1 = sim.run()
  cars1 = []
  for car in sim.cars:
    cars1.append({
      'id': car.id,
      'driving_time': car.total_driving_time,
      'done': car.done
    })

  sim._config['adaptive_routing'] = True
  sim.setup()
  history2 = sim.run()
  cars2 = []
  for car in sim.cars:
    cars2.append({
      'id': car.id,
      'driving_time': car.total_driving_time,
      'done': car.done
    })

  xs = []
  ys = []
  for i in range(len(cars2)):
    if cars1[i]['done'] and cars2[i]['done']:
      speedup = (cars1[i]['driving_time'] - cars2[i]['driving_time'])
      xs.append(i);
      ys.append(speedup)
      # print('%d: %.2f\t%.2f\t%s' % (i, cars1[i]['driving_time'], cars2[i]['driving_time'], cars1[i]['driving_time'] == cars2[i]['driving_time']))

  print('Smoothing: %s Decay: %s' % (smoothing_factor, decay_factor))
  results.append({
    'smoothing_factor': smoothing_factor,
    'decay_factor': decay_factor,
    'mean': np.mean(ys),
    'data': ys
  })
  print('Mean: %s Median: %s' % (np.mean(ys), np.median(ys)))

  # plt.plot(xs, ys, 'r+')

  # plt.title('Trip Duration Speedup')
  # plt.xlabel('Trip #')
  # plt.ylabel('Speedup (s)')
  # plt.savefig('test.pdf')

# out_file_name = args.saveas if args.saveas else 'test1.csv'

# f = open(out_file_name, 'w')

# for line in history1:
#     f.write('%s, %s, %s\n' % line)

# f.close()

# out_file_name = args.saveas if args.saveas else 'test2.csv'

# f = open(out_file_name, 'w')

# for line in history2:
#     f.write('%s, %s, %s\n' % line)

# f.close()

if __name__ == '__main__':

  config = {}
  with open('config.json', 'r') as file:
      config = json.load(file)

  config['graph_file'] = 'data/%s.graph' % args.graph_file

  sim_data = {}
  with open('data/' + args.graph_file + '.sim', 'rb') as file:
      sim_data = pickle.load(file)

  sim = Sim(config, sim_data['segments'])

  for s in smoothing_factors:
    for d in decay_factors:
      res = requests.get('%s/restart' % (config['routing_server_url']))
      run(sim, s, d)

  f = open('results.txt', 'w')
  f.write(json.dumps(results))
  f.close()

