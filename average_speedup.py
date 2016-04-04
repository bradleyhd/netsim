import argparse, json, logging, random, datetime, os.path, pickle
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

config = {}
with open('config.json', 'r') as file:
    config = json.load(file)

config['graph_file'] = 'data/%s.graph' % args.graph_file

sim_data = {}
with open('data/' + args.graph_file + '.sim', 'rb') as file:
    sim_data = pickle.load(file)

config['adaptive_routing'] = False
sim = Sim(config, sim_data['segments'])
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

f = open('results.txt', 'w')
f.write(json.dumps(ys))
f.close()

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

  pass