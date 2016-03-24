class Signal(object):

    def __init__(self, sim, graph):
      self.sim = sim
      self.graph = graph
      self.__rotations = []
      self.arcs = {}
      self.__green = {}

    def reset(self):

      for (x, y) in self.__green.keys():
        self.__green[(x, y)] = False

    def run(self):

      green_rotation_idx = 0

      while True:

        if green_rotation_idx >= len(self.__rotations):
          green_rotation_idx = 0

        # for each arc in this rotation, set it to green
        for x, y in self.__arcs():
          if (x, y) in self.__rotations[green_rotation_idx]:
            self.__set_green(x, y)

        # start running green light
        yield self.sim.env.timeout(self.sim._config['green_light_s'])

        if self.sim._config['enable_extended_green']:

          # green time left = max green time - min green time
          green_time_left = self.sim._config['max_extended_green_light_s'] - self.sim._config['green_light_s']

          # while green time left
          while(green_time_left > 0):

            empty = True
            
            # for each arc in this rotation
            for x, y in self.__arcs():

              # if there's someone at the end of the arc
              if (x, y) in self.__rotations[green_rotation_idx] and self.sim.buckets[x][y]['buckets'][-1] > 0:
                empty = False
                break

            if empty:
              break
            else:
              # wait another second
              green_time_left -= 1
              yield self.sim.env.timeout(1)

        # set all arcs to red
        self.__set_all_red()

        # let cars in intersection go during yellow light
        yield self.sim.env.timeout(self.sim._config['yellow_light_s'])

        green_rotation_idx += 1

    def __arcs(self):

      for set in range(len(self.__rotations)):
        for x, y in self.__rotations[set]:
          yield (x, y)

    def __set_green(self, x, y):

      self.__green[(x, y)] = True

      if self.sim.buckets[x][y]['buckets'][-1] > 0:
        self.sim.buckets[x][y]['buckets'][-1] -= 1

    def __set_red(self, x, y):

      self.__green[(x, y)] = False
      self.sim.buckets[x][y]['buckets'][-1] += 1

    def __set_all_red(self):

      for x, y in self.__arcs():
        if self.__green[(x, y)] == True:
          self.__green[(x, y)] = False
          self.sim.buckets[x][y]['buckets'][-1] += 1

    def addInboundArc(self, x, y):

      this_id = self.graph[x][y]['osm_way_id']
      this_name = self.graph[x][y].get('name', '')
      this_rot = -1

      for other in self.arcs.values():

        if other['id'] == this_id or other['name'] == this_name:
          this_rot = other['rotation']
          self.__rotations[this_rot].append((x, y))

      if this_rot == -1:
        self.__rotations.append([(x, y)])
        this_rot = len(self.__rotations) - 1

      self.__set_red(x, y)
          
      self.arcs[(x, y)] = {
        'id': self.graph[x][y]['osm_way_id'],
        'name': self.graph[x][y].get('name', ''),
        'rotation': this_rot,
      }
