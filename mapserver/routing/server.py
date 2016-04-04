import os, json, logging, pickle
import numpy as np

from collections import defaultdict
from copy import deepcopy
from mapserver.graph.contractor2 import GraphContractor
from mapserver.routing.router2 import Router
from networkx.readwrite import json_graph as imports
from mapserver.graph.update import GraphUpdate
from mapserver.graph.worker import Worker
from mapserver.util.timer import Timer

class Server():

  def __init__(self, config):

    self.setup(config)

    # if self.__config['realtime']:
    #   self.worker = Worker()
    #   self.worker.start()

  def setup(self, config):

    self._log = logging.getLogger(__name__)
    self.__config = config

    self.switch = 0
    self.reports = defaultdict(list)
    self.report_count = 0
    self._stats_data = {
      'repairs': []
    }

    # load graph from file
    file_path = self.__config['graph_file']
    self._log.debug('Loading graph from %s' % (file_path))
    
    with open(file_path, 'r') as file:
      
      data = json.load(file)
      graph = imports.node_link_graph(data)

    ref_graph = None

    if self.__config['reference_graph_file']:

      file_path = self.__config['reference_graph_file']
      with open(file_path, 'r') as file:
      
        data = json.load(file)
        ref_graph = imports.node_link_graph(data)

    if self.__config['sim_file']:

      sim_file_path = self.__config['sim_file']
      with open(sim_file_path, 'rb') as sim_file:
        sim_data = pickle.load(sim_file)

    self.graphs = [graph.copy()]

    if self.__config['adaptive_routing']:

      self.contractors = [
        GraphContractor(config, self.graphs[0], decision_map=sim_data['decision_route_map'], reference_graph=ref_graph)
      ]

    else:

      self.contractors = [
        GraphContractor(config, self.graphs[0])
      ]

    if self.__config['use_decision_graph']:

      self.routers = [
        Router(self.graphs[0], decision_map=sim_data['decision_route_map'])
      ]

    else:

      self.routers = [
        Router(self.graphs[0])
      ]

    self._log.debug('Graph loaded successfully.')

  def reset(self, s, d):
    self.setup(self.__config)
    self.__config['graph_weight_smoothing_factor'] = s
    self.__config['graph_weight_decay_factor'] = s

  def route(self, start, end):

    return self.routers[self.switch].route(start, end)

  def generate(self, n):

    x = np.random.choice(self.graphs[self.switch].nodes(), n)
    y = np.random.choice(self.graphs[self.switch].nodes(), n)
    # x = [6793] * n
    # y = [3535] * n

    # battleground
    # x = [322] * n
    # y = [2010] * n

    routes = []
    for i in range(n):
      routes.append(self.route(x[i], y[i]))

    return routes

  def update(self):

    if self.reports:

      timer = Timer(__name__)
      timer.start('Updating graph...')

      #self._log.debug('Processing reports: %s' % (dict(self.reports)))
      self.contractors[self.switch].repair(self.reports)
      self.reports = defaultdict(list)

      timer.stop()

    return {'ok': True }

  def report(self, start, end, duration, graph_update_frequency=None):

    # self.report_count += 1
    #self._log.debug('Received report #%d of %.2f s on %s->%s' % (self.report_count, duration, start, end))

    self.reports[(start, end)].append(duration)

    return {'ok': True }