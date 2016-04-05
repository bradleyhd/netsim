import networkx as nx
import numpy as np
import simpy as simpy
import time as time
import logging, json, collections, requests, pickle, concurrent
from networkx.readwrite import json_graph as imports
from datetime import datetime
from mapsim.simulation.car2 import Car
from mapsim.simulation.signal import Signal
from mapserver.routing.server import Server

class Sim:

  def __init__(self, server, config, routes):

    self.__log = logging.getLogger(__name__)
    self._config = config
    self.server = server
    self.orderer = 0
    self.routes = routes

    # load graph from file
    file_path = self._config['graph_file']
    self.__log.debug('Loading graph from %s...' % (file_path))
    
    with open(file_path, 'r') as file:
      
      data = json.load(file)
      self.graph = imports.node_link_graph(data)
      
    self.__log.debug('Graph loaded successfully.')
    self.__log.debug('Initializing simulation...')

    self.num_cars = self._config['num_cars']
    self.sim_duration = self._config['sim_duration']

    self.bottlenecks = self.__generate_bottlenecks()
    
    sim_file_path = self._config['sim_file']
    with open(sim_file_path, 'rb') as sim_file:
      sim_data = pickle.load(sim_file)
    self.buckets = sim_data['segments']

    # compute delays
    delay_window = (self.num_cars * 60) / self._config['cars_per_min']
    self.delays = []

    for i in range(0, self.num_cars):
      self.delays.append(np.random.randint(0, delay_window))

    # add cars
    self.cars = self.__add_cars()

    # add signals
    self.signals, self.signal_map = self.__add_signals()

  def __generate_bottlenecks(self):
    """Generates a dictionary of start_node => f where f slows the link down by a factor of f"""

    self.__log.debug('Adding bottlenecks...')
    bottlenecks = {}

    for i in range(self._config['num_bottlenecks']):

      start = np.random.choice(self.graph.nodes())
      bottlenecks[start] = self._config['bottleneck_factor']

    return bottlenecks

  def __generate_trips(self):
    """ Generates a list of trips in the form (start_time, start_node, end_node)"""

    self.__log.debug('Generating random trips...')
    trips = []

    for i in range(self.num_cars):

      #wait = np.random.randint(0, self.sim_duration / 2)
      wait = 0
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

    # res = requests.get('http://localhost:5000/routes/generate/%d' % (self.num_cars))
    # routes = res.json()
    # routes = self.server.generate(self.num_cars)

    for i in range(0, self.num_cars):

      c = Car(i, self, self.delays[i], self.routes[i])
      cars.append(c)

    return cars

  def __rerouter(self):

    import concurrent
    while True:
      
      # with concurrent.futures.ThreadPoolExecutor(max_workers=self._config['threads']) as executor:

      #   # Start the load operations and mark each future with its URL
      #   future_to_url = {executor.submit(self.__reroute, car): car for car in self.cars if car.needs_reroute == True}
      #   for future in concurrent.futures.as_completed(future_to_url):
      #     url = future_to_url[future]
      #     try:
      #         data = future.result()
            
      #     except Exception as exc:
      #         print('%r generated an exception: %s' % (url, exc))
              # sys.exit()

      cars = list([car for car in self.cars if car.needs_reroute == True])
      with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(self.__reroute, cars)

      yield self.env.timeout(0.1)

  def __reporter(self):

    while True:

      # with concurrent.futures.ThreadPoolExecutor(max_workers=self._config['threads']) as executor:

      #   # Start the load operations and mark each future with its URL
      #   future_to_url = {executor.submit(self.__report, car): car for car in self.cars}
      #   for future in concurrent.futures.as_completed(future_to_url):
      #     url = future_to_url[future]
      #     try:
      #       data = future.result()
            
      #     except Exception as exc:
      #       print('%r generated an exception: %s' % (url, exc))
      #       sys.exit()
      # with concurrent.futures.ProcessPoolExecutor() as executor:
      #   executor.map(self.__report, list([car for car in self.cars]))

      reports = []
      for car in self.cars:
        reports.extend(car.report_queue)
        car.report_queue = []

      self.server.report_bulk(reports)

      yield self.env.timeout(5)

  # @profile
  def __graph_updater(self):

    while True:

      # res = requests.get('%s/update' % (self._config['routing_server_url']))
      self.server.update()
      yield self.env.timeout(self._config['adaptive_routing_updates_s'])

  # @profile
  def location_watcher(self):

    while True:

      for car in self.cars:
        car.log_location()

      yield self.env.timeout(self._config['location_history_poll_s'])

  # @profile
  def progress_watcher(self):

    while True:

      if self.env.now > 0:

        elapsed = datetime.now() - self.setup_time
        sps = self.env.now / elapsed.total_seconds()
        # tps = elapsed / self.env.now
        steps_remaining = self._config['sim_duration'] - self.env.now
        est = steps_remaining / sps
        hours, remainder = divmod(est, 3600)
        minutes, seconds = divmod(remainder, 60)

        # pct = self.env.now / self._config['sim_duration']
        print('\rsteps: %d /sec: %0.2f %dh%dm%ds' % (self.env.now, sps, hours, minutes, seconds), end = '')

      yield self.env.timeout(5)

  def setup(self):
    """Prepares a simulation for use before a run"""

    self.__log.debug('Setting up a new simulation run...')

    self.setup_time = datetime.now()

    # decide whether to do a realtime simulation
    if self._config['realtime']:
      self.env = simpy.RealtimeEnvironment(factor=self._config['realtime_factor'], strict=True)
    else:
      self.env = simpy.Environment()

    # reset buckets
    for x in self.buckets:
      for y in self.buckets[x]:
        for i in range(len(self.buckets[x][y]['buckets'])):
          self.buckets[x][y]['buckets'][i] = 0

    for car in self.cars:
      car.reset()
      self.env.process(car.run())

    if self._config['enable_signals']:
      for signal in self.signals:
        signal.reset()
        self.env.process(signal.run())

    if self._config['enable_location_history']:
      self.env.process(self.location_watcher())

    if self._config['adaptive_routing']:
      self.env.process(self.__graph_updater())
      # self.env.process(self.__rerouter())
      # self.env.process(self.__reporter())

    self.env.process(self.progress_watcher())

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
