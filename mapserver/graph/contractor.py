from mapserver.util.pq import PriorityQueue
from mapserver.util.timer import Timer
import itertools, logging, sys
import networkx as nx

class GraphContractor(object):

    def __init__(self, config, G):

        self.__log = logging.getLogger(__name__)

        self.G = G
        self.num_nodes = self.G.number_of_nodes()
        self.x_node_pq = PriorityQueue()
        self.updates = {}

        self.__weight_label = config['graph_weight_label']
        self.__smoothing_factor = config['graph_weight_smoothing_factor']
        self.__decay_factor = config['graph_weight_decay_factor']

    def unpack(self, previous, s, t):

        current_node = t
        path = []

        while current_node != s:
            previous_node = previous[current_node][1]
            path.append((previous_node, current_node))
            current_node = previous_node

        path.reverse()
        return path

    def _successors(self, x, simulated=False):

        if simulated:
            return ((y, data) for y, data in iter(self.G.edge[x].items()) if not self.G.node[y]['priority'] < sys.maxsize)
        else:
            x_pri = self.G.node[x]['priority']
            return ((y, data) for y, data in iter(self.G.edge[x].items()) if self.G.node[y]['priority'] > x_pri)

    # searches for shortest paths from start_node to each of the target_nodes
    # while excluding the ignore_node
    # successful searches are witness paths
    # general structure of a path is v->u->w
    # direct costs is a list of the costs of going directly via ignore_node
    # ignore node MUST have a priority set

    #@profile
    def _local_search(self, start_node, ignore_node, end_nodes, direct_costs, simulated=True, log=False):

        self._local_search_pq = PriorityQueue()

        # add start_node with cost 0
        self._local_search_pq.push(0, start_node)

        # key = node value = (cost_to_node, predecessor)
        cost_and_predecessor = {}

        # initial values
        max_cost = max(direct_costs)
        cost_and_predecessor[start_node] = (0, None)

        priority = self.G.node[ignore_node]['priority']

        while True:

            # pop the next node from the queue
            # the priority value here is the cost to the node
            try:
                current_cost, current_node = self._local_search_pq.pop()
            except KeyError as e:
                break

            # exit if the frontier has already exceeded a cost that would yield
            # a witness path
            if current_cost > max_cost:
                break

            # exit if we have settled all end nodes
            if set(end_nodes) <= cost_and_predecessor.keys():
                break

            for neighbor_node, edge_tags in self._successors(current_node, simulated):

                # compute the tentative cost to the current neighbor
                new_cost = current_cost + edge_tags[self.__weight_label]

                # if the neighbor has not yet been examined or a cheaper path to the neighbor has been found
                if neighbor_node not in cost_and_predecessor or new_cost < cost_and_predecessor[neighbor_node][0]:

                    # insert/update the queue, priority = new_cost
                    self._local_search_pq.push(new_cost, neighbor_node)

                    # update the dictionary to link current -> neighbor
                    cost_and_predecessor[neighbor_node] = (new_cost, current_node)


        # list of end_nodes that ARE the shortest/only path
        # these will need a shortcut added
        sp_ends = []

        # for each withness path from start_node to a end_node
        for i in range(0, len(end_nodes)):

            end_node = end_nodes[i]

            # if end_node wasn't reach before the search terminated
            # either a limit was exceeded or there's no other shortest path
            if end_node not in cost_and_predecessor:
                sp_ends.append(end_node)

            # if the witness path cost <= the cost of start->ignore->end
            # then the witness path is a viable alternative
            # if not, then we need to add a shortcut for the orignal path
            elif cost_and_predecessor[end_node][0] > direct_costs[i]:
                sp_ends.append(end_node)

                # on the fly edge reduction
                # if the shortest path found isn't shorter than the direct costs
                # and yet theres' a direct edge, delete the edge
                if not simulated and end_node in self.G[start_node]:
                    self.G.remove_edge(start_node, end_node)

        # return the size of the search space and the terminuses of needed shortcuts
        return (len(cost_and_predecessor), sp_ends)

    #@profile
    def _calc_node_priority(self, v):

        total_search_size = 0
        total_num_shortcuts = 0

        # for each predecessor of v
        # do a local search to all successors of v
        # there's no need to check the priority of the successors/predecessors
        # because either it doesn't matter or the calling method does it first
        for u, u_edge in iter(self.G.pred[v].items()):

            w_nodes = []
            uvw_costs = []

            for w, w_edge in iter(self.G.succ[v].items()):

                if w == u:
                    continue

                w_nodes.append(w)
                uvw_costs.append(u_edge[self.__weight_label] + w_edge[self.__weight_label])

            # if there are any successors
            if w_nodes:
                search_size, sp_ends = self._local_search(u, v, w_nodes, uvw_costs)
                total_search_size += search_size
                total_num_shortcuts += len(sp_ends)

        # compute the number of neighbors in the remaining graph
        # if n is in the remaining graph or if v doesn't have a priority
        # then everything is above it in the ordering

        v_priority = self.G.node[v]['priority']

        # v will not be ranked whenever nodes are first ordered
        # v will be ranked on any recalculation of priority
        v_has_priority = (v_priority != sys.maxsize)

        num_neighbors = 0
        for n in nx.all_neighbors(self.G, v):
            if self.G.node[n]['priority'] > v_priority or not v_has_priority:
                num_neighbors += 1

        # compute the edge difference
        # edge difference = shortcuts - contractable "remaining" incident edges
        # edge_diff = total_num_shortcuts - num_neighbors

        # compute the priority
        priority = (total_num_shortcuts - num_neighbors) + total_search_size + (3 * self.G.node[v]['adj_count'])

        return priority

    def order_nodes(self):

        self._node_priority_pq = PriorityQueue()

        timer = Timer(__name__)
        timer.start('Ordering nodes...')

        for v in self.G.nodes():

            priority = self._calc_node_priority(v)
            self._node_priority_pq.push(priority, v)

        timer.stop()
        self.__log.info('%d nodes, %.10f ms/node' % (self.num_nodes, timer.elapsed / self.num_nodes))

    # def re_order_nodes(self):

    #     pq_copy = FastUpdateBinaryHeap(self.num_nodes, self.num_nodes + 1)

    #     while self._node_priority_pq.count:

    #         _, v = self._node_priority_pq.pop()
    #         priority = self._calc_node_priority(v)
    #         pq_copy.push(priority, v)

    #     self._node_priority_pq = pq_copy

    def __complete_early_contraction(self, count):

        while self._node_priority_pq.count:

            _, v = self._node_priority_pq.pop()
            self.G.node[v]['priority'] = count
            count += 1

    def update(self, s, t, weight):

        if not (s, t) in self.updates:
            self.updates[(s, t)] = []

        self.updates[(s, t)].append(weight)
        if s == 1899:
            print('update: %s->%s %s' % (s, t, weight))

    def repair(self, reports):

        # reset the contraction priority queue
        self._node_priority_pq = PriorityQueue()

        for x, y, e in self.G.edges(data = True):

            if 'real_arc' in e:
                new_weight = max(e['default_ttt'], (e['ttt'] * self.__decay_factor))

                if (x, y) in reports:

                    updates = reports[(x, y)]
                    new_weight = sum(updates) / len(updates)

                weight = (self.__smoothing_factor * new_weight) + ((1 - self.__smoothing_factor) * e['ttt'])

                # if x == 1899:
                # if (x, y) in self.updates:
                #     print('%s -> %s default: %s, current %s, new %s, final %s' % (x, y,e['default_ttt'], e['ttt'], new_weight, weight))

                e['ttt'] = weight
                e['real_ttt'] = weight








        # if not self.updates:
        #     return

        # find the threshold priority
        # threshold = -1
        # for (x, y), weights in self.updates.items():

        #     if x == 1899:
        #         print(weights)

        #     # compute the average weight
        #     new_weight = sum(weights) / len(weights)
        #     if x == 1899: #or x == 7041:
        #         print('new weight %s->%s %s->%s' % (x, y, self.G[x][y]['ttt'], new_weight))

        #     # use exponential smoothing
        #     weight = (self.__SMOOTHING_FACTOR * new_weight) + ((1 - self.__SMOOTHING_FACTOR) * self.G[x][y]['ttt'])
        #     if x == 1899: #or x == 7041:
        #         print('weight %s->%s %s->%s' % (x, y, self.G[x][y]['ttt'], weight))

        #     # find the lowest priority for each end of the segment and compare
        #     # to global minimum
        #     tmp = min(self.G.node[x]['priority'], self.G.node[y]['priority'])
        #     if tmp < threshold or threshold == -1:
        #         threshold = tmp

        #     # update edge weight
        #     self.G[x][y]['ttt'] = weight
        #     self.G[x][y]['real_ttt'] = weight

        # invalidate all affected shortcuts
        for x, y, edge in self.G.edges(data = True):

            if edge['is_shortcut']:

                priority = self.G.node[edge['repl_node']]['priority']

                #if priority >= threshold:

                if 'real_arc' in edge:

                    edge['is_shortcut'] = False
                    edge['ttt'] = edge['real_ttt']
                    del edge['repl_node']

                else:

                    self.G.remove_edge(x, y)

        # enqueue all affected nodes for contraction
        for n, d in self.G.nodes(data = True):

            #if d['priority'] >= threshold:
            self._node_priority_pq.push(d['priority'], n)

        # repair the graph
        self.contract_graph(False)
        self.set_flags()

        # reset updates queue
        self.updates = {}

    # @profile
    def contract_graph(self, firstRun=True):

        timer = Timer(__name__)
        timer.start('Contracting graph...')

        count = 0

        while True:

            try:
                v_priority, v = self._node_priority_pq.pop()
            except KeyError as e:
                break

            if firstRun:
                self.G.node[v]['priority'] = count
                v_priority = count

            #print('popped node %s - %d' % (v, v_priority))

            if count % 50 == 0:
                print('\r%.4f%%' % ((count / self.num_nodes) * 100), end = '')

            #if count % 1000 == 0:
                #self.re_order_nodes()

            neighbors = set()
            count += 1
            v_ct = 0

            #print('---NODE---')
            #print('%d with priority %d' % (v, self.G.node[v]['priority']))

            # for each predecessor of v to each successor v
            for u, u_edge in self.G.pred[v].items():

                # if the predecessor edge is not of a higher priority, skip it
                if firstRun and self.G.node[u]['priority'] != sys.maxsize:
                    continue

                if (not firstRun) and self.G.node[u]['priority'] <= v_priority:
                    continue

                neighbors.add(u)
                w_nodes = []
                uvw_costs = []

                #print('pred %d with priority %d' % (u, self.G.node[u]['priority']))

                for w, w_edge in self.G.succ[v].items():

                    if u == w:
                        continue

                    # if the succssor edge is not of a higher priority, skip it
                    if firstRun and self.G.node[w]['priority'] != sys.maxsize:
                        continue
                    
                    if (not firstRun) and self.G.node[w]['priority'] <= v_priority:
                        continue

                    #print('succ %d with priority %d' % (w, self.G.node[w]['priority']))

                    #print('%d->%d %s' % (u, v, u_edge['is_shortcut']))
                    #print('%d->%d %s' % (v, w, w_edge['is_shortcut']))

                    neighbors.add(w)
                    w_nodes.append(w)
                    uvw_costs.append(u_edge[self.__weight_label] + w_edge[self.__weight_label])

                # if there are successors (which make a complete uvw path)
                if w_nodes:

                    v_ct += len(w_nodes)

                    # local search to get which paths need shortcuts
                    _, ends = self._local_search(u, v, w_nodes, uvw_costs, firstRun, False)

                    # for each path add a shortcut
                    for end in ends:

                        weight = u_edge[self.__weight_label] + self.G[v][end][self.__weight_label]

                        tags = {
                            self.__weight_label: weight,
                            'is_shortcut': True,
                            'repl_node': v,
                        }

                        #print('adding %s->%s (%s)' % (u, end, weight))
                        self.G.add_edge(u, end, **tags)

            # update counts of neighbors
            # only neighbors in the remaining graph were added, so no explicit
            # check needed
            #print('updating %s neighbors' % len(neighbors))
            if firstRun:
                for n in neighbors:

                    self.G.node[n]['adj_count'] += 1
                    new_priority = self._calc_node_priority(n)
                    self._node_priority_pq.push(new_priority, n)

            #print('node: %d, inspecting %d' % (v, v_ct))

        print('\r%.4f%%' % 100)
        timer.stop()

    def set_flags(self):

        for u, v, edge_data in self.G.edges_iter(data = True):

                u_priority = self.G.node[u]['priority']
                v_priority = self.G.node[v]['priority']

                # for edge going from u -> v
                if u_priority < v_priority:
                    edge_data['level'] = 1
                    edge_data['up'] = True
                elif u_priority > v_priority:
                    edge_data['level'] = -1
                    edge_data['down'] = True
                else:
                    print('wtf %s %s' % (u, v))
