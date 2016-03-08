import asyncio, logging

class GraphUpdate(object):

  def __init__(self, worker, server, reports):

    self.__log = logging.getLogger(__name__)
    self.worker = worker
    self.server = server
    self.reports = reports

  def do(self):

    self.worker.enqueue(self._process, self._process_callback)

  def _update(self):

    online = self.server.switch
    offline = 1 - self.server.switch

    # copy online graph into offline graph
    # .copy() is the networkx deep copy implementation
    self.server.graphs[offline] = self.server.graphs[online].copy()

    # repair the offline graph
    self.server.contractors[offline].repair(self.reports)

    # take original graph back online
    online = 1 - self.server.switch
    self.__log.debug('Taking %d back online' % (online))
    self.server.switch = online

    self.__log.debug('Graph update complete')

  @asyncio.coroutine
  def _process(self):

    with (yield from self.worker.limit_simultaneous_processes):
      self._update()

  def _process_callback(self, future):
    pass
    