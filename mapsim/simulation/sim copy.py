import networkx as nx
import numpy as np
import simpy as simpy
import time as time
import logging, json
from networkx.readwrite import json_graph as imports
from datetime import datetime
from mapsim.simulation.car import Car
from mapsim.simulation.signal import Signal

class Sim:

  def __init__(self, config, buckets):

    self.__log = logging.getLogger(__name__)
    self.__config = config

    # load graph from file
    file_path = self.__config['graph_file']
    self.__log.debug('Loading graph from %s...' % (file_path))
    
    with open(file_path, 'r') as file:
      
      data = json.load(file)
      self.graph = imports.node_link_graph(data)
      
    self.__log.debug('Graph loaded successfully.')
    self.__log.debug('Initializing simulation...')

    self.num_cars = self.__config['num_cars']
    self.sim_duration = self.__config['sim_duration']

    self.bottlenecks = self.__generate_bottlenecks()
    self.trips = self.__generate_trips()
    self.buckets = buckets
    self.adaptive = False


  def __generate_bottlenecks(self):
    """Generates a dictionary of start_node => f where f slows the link down by a factor of f"""

    self.__log.debug('Adding bottlenecks...')
    bottlenecks = {}

    for i in range(self.__config['num_bottlenecks']):

      start = np.random.choice(self.graph.nodes())
      bottlenecks[start] = self.__config['bottleneck_factor']

    return bottlenecks

  def __generate_trips(self):
    """ Generates a list of trips in the form (start_time, start_node, end_node)"""

    self.__log.debug('Generating random trips...')
    trips = []

    for i in range(self.num_cars):

      wait = np.random.randint(0, self.sim_duration / 2)
      #wait = 0
      start = np.random.choice(self.graph.nodes())
      end = np.random.choice(self.graph.nodes())
      trips.append((wait, start, end))

    return trips

  def __add_signals(self):
    """Attaches signal instances to the appropriate intersections on the graph"""

    self.__log.debug('Adding traffic signals...')
    signals = []
    signal_map = {}

    for n, data in self.graph.nodes(data = True):

      if 'traffic_signal' in data:

        if n not in signal_map:
        #if not self.graph.node[n].get('signal_obj', False):
          s = Signal(self, self.graph)
          # self.graph.node[n]['signal_obj'] = s
          signals.append(s)
          signal_map[n] = s

        # add new signal only if adjacent signal isn't found
        for s in self.graph.successors_iter(n):

          if self.graph[n][s]['is_shortcut']:
            continue

          if 'traffic_signal' in self.graph.node[s]:
          #if s not in signal_map:
            #self.graph.node[n]['signal_obj'] = self.graph.node[s]['signal_obj']
            signal_map[s] = signal_map[n]
            #break

        for p in self.graph.predecessors_iter(n):

          if self.graph[p][n]['is_shortcut']:
            continue

          if 'traffic_signal' in self.graph.node[p]:
          #if self.graph.node[p].get('signal_obj', False):
            #self.graph.node[n]['signal_obj'] = self.graph.node[p]['signal_obj']
            signal_map[p] = signal_map[n]
            #break

    for x, y, e in self.graph.edges(data=True):

      if not e['is_shortcut'] and y in signal_map:

        s = signal_map[y]

        # only add arc if this is the first in a set
        if 'traffic_signal' not in self.graph.node[x]:
          s.addInboundArc(x, y)

    return signals, signal_map

  def __add_cars(self):
    """Initializes cars and requests an intial route for each one"""

    self.__log.debug('Adding cars and calculating intial routes...')
    cars = []

    for i in range(0, self.num_cars):

      delay, start, end = self.trips[i]
      c = Car(i, self, delay, start, end)

      cars.append(c)

    return cars

  def setup(self, adaptive=False):
    """Prepares a simulation for use before a run"""

    self.__log.debug('Setting up a new simulation run...')

    self.setup_time = datetime.now()
    self.adaptive = adaptive

    self.cars = self.__add_cars()

    if self.__config['signals']:
      self.signals, self.signal_map = self.__add_signals()

    # decide whether to do a realtime simulation
    if self.__config['realtime']:
      self.env = simpy.RealtimeEnvironment(factor=self.__config['realtime_factor'], strict=True)
    else:
      self.env = simpy.Environment()

    for car in self.cars:
      self.env.process(car.run())

    if self.__config['signals']:
      for signal in self.signals:
        self.env.process(signal.run())

  def run(self):
    """Runs the simulation"""

    self.__log.debug('Running simulation...')
    start_time = time.perf_counter()

    #for i in range(1, self.sim_duration):
    self.env.run(until = self.sim_duration)
     # break

    history = []
    for c in self.cars:
      history.extend(c.history)

    self.__log.debug('Simulation complete in %.2f ms.' % ((time.perf_counter() - start_time) * 1000))

    return history
