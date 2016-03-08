class Signal(object):

    YELLOW_LIGHT_MS = 5000
    GREEN_LIGHT_MS = 30000

    def __init__(self, sim, graph):
      self.sim = sim
      self.graph = graph
      self.rotation = []
      self.arcs = {}

    def run(self):

      go_idx = 0

      # print(self.rotation)

      while True:

        if go_idx >= len(self.rotation):
          go_idx = 0

        #print('---\nlights changed at %s' % (id(self)))

        for set in range(len(self.rotation)):
          for x, y in self.rotation[set]:
            if set == go_idx:
              self.arcs[(x, y)]['can_go'] = True
              #print('%s go' % self.arcs[(x, y)].get('name', 'none'))
            else:
              self.arcs[(x, y)]['can_go'] = False
              #print('%s NO go' % self.arcs[(x, y)].get('name', 'none'))
       
        # print(self.rotation)
        # print(self.arcs)
        yield self.sim.env.timeout(self.GREEN_LIGHT_MS)
        go_idx += 1
        yield self.sim.env.timeout(self.YELLOW_LIGHT_MS)

      # print(self.arcs)

    #@profile
    def canGo(self, x, y):

      try:
        return True if self.arcs[(x, y)]['can_go'] else False
      except KeyError:
        return True
      # arc = self.arcs.get((x, y), None)
      # if (arc):
      #   return arc['can_go']
      # else:
      #   return True

      #return Ture

    def addInboundArc(self, x, y):



      this_id = self.graph[x][y]['osm_way_id']
      this_name = self.graph[x][y].get('name', '')
      this_rot = -1

      for other in self.arcs.values():

        if other['id'] == this_id or other['name'] == this_name:
          this_rot = other['rotation']
          self.rotation[this_rot].append((x, y))

      if this_rot == -1:
        self.rotation.append([(x, y)])
        this_rot = len(self.rotation) - 1
          
      self.arcs[(x, y)] = {
        'id': self.graph[x][y]['osm_way_id'],
        'name': self.graph[x][y].get('name', ''),
        'rotation': this_rot,
        'can_go': False,
      }
      
    
