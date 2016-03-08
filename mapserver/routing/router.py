import logging
import math, random

from mapserver.util.pq import PriorityQueue

class Router():

    def __init__(self, G, weight_label = 'ttt'):

        super().__init__()
        self.__log = logging.getLogger(__name__)
        
        self.G = G
        self.weight_label = weight_label

        self.short_path = []
        self.touch_path_fwd = []
        self.touch_path_bwd = []
        self.exact = True
        self.opt = 0

    def route(self, start_node, end_node):

        #self._timer_begin()

        path = self._bidirectional_dijkstra(start_node, end_node)
        #self._timer_end()

        #path = id(self)

        return path

    def _backwards_neighbors(self, node):

        return ((n, edge[self.weight_label]) for n, edge in self.G.pred[node].items() if 'down' in edge)

    def _forwards_neighbors(self, node):

        return ((n, edge[self.weight_label]) for n, edge in self.G.succ[node].items() if 'up' in edge)

    def _neighbors(self, r, node):

        if r == 0:
            return self._forwards_neighbors(node)
        else:
            return self._backwards_neighbors(node)

    def _anti_neighbors(self, r, node):

        if r == 1:
            return self._forwards_neighbors(node)
        else:
            return self._backwards_neighbors(node)

    def _stall_bfs(self, r, u, dist_to_u, dist_to_u_via_v, source, stalled):

        # stall node u
        stalled[r][u] = dist_to_u_via_v

        # a queue
        q = []

        # enqueue all of u's neighbors with tentative distances
        q.extend([(x, dist_to_u + dist_u_x) for x, dist_u_x in self._neighbors(r, u)])

        while q:

            # pop the next node
            n, dist_to_n = q.pop()

            # if n is already stalled, continue
            if n in stalled[r]: continue

            # if n is settled and our current path to n isn't shorter, continue
            if n in source[r] and dist_to_n >= source[r][n][0]: continue

            # stall node n
            stalled[r][n] = dist_to_n
            #stall_count += 1

            # queue all neighbors
            q.extend([(o, dist_to_n + dist_n_o) for o, dist_n_o in self._neighbors(r, n)])

    def _bidirectional_dijkstra(self, start_node, end_node):

        self.short_path = []
        self.touch_path_fwd = []
        self.touch_path_bwd = []

        # r = 0 for forward search, 1 for backward search
        r = 1

        # reset queues
        self._forward_pq = PriorityQueue()
        self._backward_pq = PriorityQueue()

        # set up queues
        qs = [self._forward_pq, self._backward_pq]

        # add start_node with cost 0 to forward search
        qs[0].push(0, start_node)

        # add end_node with cost 0 to backward search
        qs[1].push(0, end_node)

        # dictionary visted node -> (cost to node from start, previous node)
        source = [{}, {}]
        source[0][start_node] = (0, None)
        source[1][end_node] = (0, None)

        stalled = [{}, {}]

        best_dist = math.inf
        best_node = None

        # store all possible paths
        all_nodes = {}

        stalled_count = 0

        # while the queues are not empty
        while qs[0].not_empty() or qs[1].not_empty():

            # if the smallest cost to node in either queue is bigger than the
            # shortest path distance, we can halt
            if best_dist <= min(qs[0].min_val(), qs[1].min_val()): break

            # if the other queue is not empty, switch directions
            if qs[1 - r].not_empty(): r = 1 - r

            # pop the minimum node
            try:
                dist_to_u, u = qs[r].pop()
            except KeyError as e:
                break

            # if node has been settled by both searches
            if u in source[1 - r]:

                # best candidate distance is the min of the previous best
                # candidate and the path through u
                dist_via_u = dist_to_u + source[1-r][u][0]
                all_nodes[u] = dist_via_u

                if dist_via_u < best_dist:
                    best_dist = dist_via_u
                    best_node = u

            # look at all neighbors of the wrong gradient
            # for forwards search, inspect the downward edge_dist
            # for v, dist_u_v in self._anti_neighbors(r, u):

            #     dist_to_u_via_v = dist_u_v + source[r].get(v, (math.inf, None))[0]
            #     if dist_to_u > dist_to_u_via_v:

            #         self._stall_bfs(r, u, dist_to_u, dist_to_u_via_v, source, stalled)
            #         break

            # if u is stalled
            # if u in stalled[r]: continue

            # search
            for v, edge_dist in self._neighbors(r, u):

                # print('dir: %d examining %d->%d' % (r, u, v))
                if r == 0:
                    self.touch_path_fwd.extend([(u, v)])
                else:
                    self.touch_path_bwd.extend([(v, u)])

                # compute tentative distance
                dist_to_v_via_u = dist_to_u + edge_dist

                # if v has not been settled or a shorter path has been found
                if v not in source[r] or dist_to_v_via_u < source[r][v][0]:

                    # insert/update the queue, priority = new_cost
                    qs[r].push(dist_to_v_via_u, v)

                    # update the dictionary to link current -> neighbor
                    source[r][v] = (dist_to_v_via_u, u)

                    # if v is stalled, unstall it
                    if v in stalled[r]: del stalled[r][v]

        if not best_node: return []

        if not self.exact:
            choices = []
            #print(all_nodes)
            for key in sorted(all_nodes, key=all_nodes.get):
                choices.append(key)
            #print(choices)

            if len(choices) < 1:
                return []
        
            #best_node = random.choice(choices[0:2])
            best_node = choices[self.opt]

        route =  self.__path_unpack(source[0], start_node, best_node) + self.__path_unpack(source[1], end_node, best_node, forwards_search = False)

        if not self.exact:

            #experimental cycle detection
            route = self.__scrub_cycles(route)    

        # for i in range(len(route)-1):
        #     (x, y) = route[i]
        #     (x1, y1) = route[i+1]
        #     rd = self.G[x][y].get('name', '?')
        #     nrd = self.G[x1][y1].get('name', '?')
        #     print('%d %d: %s->%s' % (x, y, rd, nrd))

        # print('---')

        return route

    def __scrub_cycles(self, route):

        tmp = route.copy()
        for i in range(len(route)-1):

            left = i
            right = i + 1

            (a, b) = route[left]
            (c, d) = route[right]
            
            found = False
            if c == b and d == a:

                found = True
                left -= 1
                right += 1

                while c == b and d == a and left >= 0 and right < len(route) - 1:

                    left -= 1
                    right += 1
                    (a, b) = route[left]
                    (c, d) = route[right]
                    

            if found:
                left += 1
                # print('deleting %s' % tmp[left:right])
                del tmp[left:right]
                return self.__scrub_cycles(tmp)

        return tmp


    def __uncontract_forwards(self, ref_start, ref_end):

        # if there is a contracted node, recursively search for more contracted nodes
        if 'repl_node' in self.G[ref_end][ref_start]:
            node = self.G[ref_end][ref_start]['repl_node']
            return self.__uncontract_forwards(ref_start, node) + self.__uncontract_forwards(node, ref_end)

        return [(ref_end, ref_start)]

    def __uncontract_backwards(self, ref_start, ref_end):

        # if there is a contracted node, recursively search for more contracted nodes
        if 'repl_node' in self.G[ref_start][ref_end]:
            node = self.G[ref_start][ref_end]['repl_node']
            return self.__uncontract_backwards(ref_start, node) + self.__uncontract_backwards(node, ref_end)

        return [(ref_start, ref_end)]

    def __path_unpack(self, previous, search_start, search_end, forwards_search = True):

        current_node = search_end
        path = []

        while current_node != search_start:

            previous_node = previous[current_node][1]

            if forwards_search:
                self.short_path.extend([(previous_node, current_node)])
                full_path = self.__uncontract_forwards(current_node, previous_node)
            else:
                self.short_path.extend([(current_node, previous_node)])
                full_path = self.__uncontract_backwards(current_node, previous_node)
                

            path.extend(full_path)
            current_node = previous_node

        if forwards_search:
            path.reverse()

        return path
