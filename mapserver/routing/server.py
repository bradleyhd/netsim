import os, json, logging, pickle
from collections import defaultdict
from copy import deepcopy
from mapserver.graph.contractor import GraphContractor
from mapserver.routing.router import Router
from networkx.readwrite import json_graph as imports
from mapserver.graph.update import GraphUpdate
from mapserver.graph.worker import Worker
from mapserver.util.timer import Timer

class Server():

  def __init__(self, config):

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

      self.base_graph = graph
      self.graphs = [graph.copy(), graph.copy()]

      self.contractors = [
        GraphContractor(config, self.graphs[0]),
        GraphContractor(config, self.graphs[1])
      ]

      if self.__config['decision_graph']:

        sim_file_path = self.__config['sim_file']
        with open(sim_file_path, 'rb') as sim_file:

          sim_data = pickle.load(sim_file)

          self.base_router = Router(self.base_graph, decision_map=sim_data['decision_route_map'])

          self.routers = [
            Router(self.graphs[0], decision_map=sim_data['decision_route_map']),
            Router(self.graphs[1], decision_map=sim_data['decision_route_map'])
          ]

      else:
        self.base_router = Router(self.base_graph)
        self.routers = [Router(self.graphs[0]), Router(self.graphs[1])]

    self._log.debug('Graph loaded successfully.')

    if self.__config['realtime']:
      self.worker = Worker()
      self.worker.start()

  def route(self, start, end, adaptive=False):

    if adaptive:
      return self.routers[self.switch].route(start, end)
    else:
      return self.base_router.route(start, end)

  def report(self, start, end, duration, graph_update_frequency=None):

    self.report_count += 1
    self._log.debug('Received report #%d of %.2f ms on %s->%s' % (self.report_count, duration, start, end))

    self.reports[(start, end)].append(duration)

    if graph_update_frequency is None:
      graph_update_frequency = self.__config['graph_update_frequency']

    # if it is time to update
    if self.report_count >= graph_update_frequency:

      self._log.debug('Updating graph...')

      if self.__config['realtime']:

        # make a copy of the reports
        reports = deepcopy(self.reports)
        self._log.debug('Processing reports: %s' % (dict(reports)))

        offline = self.switch
        online = 1 - self.switch

        # take other graph online
        self._log.debug('Taking %d online and %d offline' % (online, offline))
        self.switch = online

        g = GraphUpdate(self.worker, self, reports)
        g.do()

      else:

        timer = Timer(__name__)
        timer.start('Updating graph...')

        self._log.debug('Processing reports: %s' % (dict(self.reports)))
        self.contractors[self.switch].repair(self.reports)

        timer.stop()
        
      self._stats_data['repairs'].append((self.report_count, timer.elapsed))

      # reset report count
      self.report_count = 0

      # reset reports
      self.reports = defaultdict(list)

    return {'ok': True }