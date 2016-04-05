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

def get_route(id):
  return server.generate_random()

def run(config):

  # get routes
  import concurrent
  ids = range(config['num_cars'])
  routes = []
  with concurrent.futures.ProcessPoolExecutor() as executor:
    for car_id, route in zip(ids, executor.map(get_route, ids)):
      routes.append(route)

  # for id in ids:
  #   routes.append(server.generate_random())

  config = copy.deepcopy(config)
  config['graph_file'] = 'data/%s.graph' % args.graph_file

  config['adaptive_routing'] = False
  sim = Sim(server, config, routes)
  sim.setup()
  history1 = sim.run()
  cars1 = []
  for car in sim.cars:
    cars1.append({
      'id': car.order,
      'driving_time': car.total_driving_time,
      'done': car.done
    })

  sim._config['adaptive_routing'] = True
  sim.setup()
  history2 = sim.run()
  cars2 = []
  for car in sim.cars:
    cars2.append({
      'id': car.order,
      'driving_time': car.total_driving_time,
      'done': car.done
    })

  cars = []
  before_times = []
  after_times = []
  speedups = []
  for i in range(len(cars2)):
    if cars1[i]['done'] and cars2[i]['done']:
      
      before_times.append(cars1[i]['driving_time'])
      after_times.append(cars2[i]['driving_time'])

      cars.append(cars1[i]['id']);
      speedup = (cars1[i]['driving_time'] - cars2[i]['driving_time'])
      speedups.append(speedup)
      # print('%d: %.2f\t%.2f\t%s' % (i, cars1[i]['driving_time'], cars2[i]['driving_time'], cars1[i]['driving_time'] == cars2[i]['driving_time']))

  f = open('results.txt', 'w')
  f.write(json.dumps(cars))
  f.write('\n')
  f.write(json.dumps(before_times))
  f.write('\n')
  f.write(json.dumps(after_times))
  f.write('\n')
  f.write(json.dumps(speedups))
  f.write('\n')
  f.close()

  if speedups:
    print(np.mean(speedups))

  # plt.plot(xs, ys, 'r+')

  # plt.title('Trip Duration Speedup')
  # plt.xlabel('Trip #')
  # plt.ylabel('Speedup (s)')
  # plt.savefig('test.pdf')

  out_file_name = args.saveas if args.saveas else 'test1.csv'

  f = open(out_file_name, 'w')

  for line in history1:
      f.write('%s, %s, %s\n' % line)

  f.close()

  out_file_name = args.saveas if args.saveas else 'test2.csv'

  f = open(out_file_name, 'w')

  for line in history2:
      f.write('%s, %s, %s\n' % line)

  f.close()


if __name__ == '__main__':

  run(config)
