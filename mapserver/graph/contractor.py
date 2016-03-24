from mapserver.util.pq import PriorityQueue
from mapserver.util.timer import Timer

import itertools, logging, sys
import networkx as nx

class GraphContractor(object):

    def __init__(self, config, G, decision_map=None, reference_graph=None):

        self.__log = logging.getLogger(__name__)
        self.__config = config

        self.G = G
        self.num_nodes = self.G.number_of_nodes()
        self.x_node_pq = PriorityQueue()
        self.decision_map = decision_map
        self.reference_graph = reference_graph

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

    def _successors(self, x, initialize=False):

        if initialize:
            return ((y, data) for y, data in iter(self.G.succ[x].items()) if not self.G.node[y]['priority'] < sys.maxsize)
        else:
            x_pri = self.G.node[x]['priority']
            return ((y, data) for y, data in iter(self.G.succ[x].items()) if self.G.node[y]['priority'] > x_pri)

    def _predecessors(self, y, initialize=False):

        if initialize:
            return ((x, data) for x, data in iter(self.G.pred[y].items()) if not self.G.node[x]['priority'] < sys.maxsize)
        else:
            y_pri = self.G.node[y]['priority']
            return ((x, data) for x, data in iter(self.G.pred[y].items()) if self.G.node[x]['priority'] > y_pri)

    # searches for shortest paths from start_node to each of the target_nodes
    # while excluding the ignore_node
    # successful searches are witness paths
    # general structure of a path is v->u->w
    # direct costs is a list of the costs of going directly via ignore_node
    # ignore node MUST have a priority set

    #@profile
    def _local_search(self, start_node, ignore_node, end_nodes, direct_costs, initialize=True, log=False):

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

            for neighbor_node, edge_tags in self._successors(current_node, initialize):

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
                # if end_node in self.G[start_node]:
                #     self.G.remove_edge(start_node, end_node)

        # return the size of the search space and the terminuses of needed shortcuts
        return (len(cost_and_predecessor), sp_ends)

    #@profile
    def _calc_node_priority(self, v, initialize=True):

        if self.__config['use_fast_contract']:

            return len(list(self._predecessors(v, initialize))) + len(list(self._successors(v, initialize)))

        total_search_size = 0
        total_num_shortcuts = 0
        neighbors = set()

        for u, u_edge in self._predecessors(v, initialize):

            neighbors.add(u)
            w_nodes = []
            uvw_costs = []

            for w, w_edge in self._successors(v, initialize):

                if w == u:
                    continue

                neighbors.add(w)

                w_nodes.append(w)
                uvw_costs.append(u_edge[self.__weight_label] + w_edge[self.__weight_label])

            # if there are any successors
            if w_nodes:
                search_size, sp_ends = self._local_search(u, v, w_nodes, uvw_costs, initialize)
                total_search_size += search_size
                total_num_shortcuts += len(sp_ends)

        num_neighbors = len(neighbors)

        # compute the priority
        priority = (total_num_shortcuts - num_neighbors) + (3 * self.G.node[v]['adj_count']) + total_search_size 

        return priority

    #@profile
    def order_nodes(self):

        self._node_priority_pq = PriorityQueue()

        timer = Timer(__name__)
        timer.start('Ordering nodes...')


        for v in self.G.nodes_iter():

            priority = self._calc_node_priority(v)
            self._node_priority_pq.push(priority, v)

        timer.stop()
        self.__log.info('%d nodes, %.10f ms/node' % (self.num_nodes, timer.elapsed / self.num_nodes))

    def repair(self, reports):

        # if using a decisiong graph
        if self.__config['use_decision_graph']:

            # for each edge
            for u, v, e in self.G.edges(data = True):

                # if it's a shortcut, invalidate it
                if not 'real_arc' in e:

                    self.G.remove_edge(u, v)

                else:

                    # if a real edge is also a shortcut, reset it
                    if e['is_shortcut']:
                        e['is_shortcut'] = False
                        e['ttt'] = e['real_ttt']
                        del e['repl_node']

                    # new_ttt = 0

                    # for each edge in the orignal graph
                    arc_weight = 0
                    for x, y in self.decision_map[(u, v)]:

                        z = self.reference_graph[x][y]

                        # if the edge has a report, integrate it
                        if (x, y) in reports:

                            updates = reports[(x, y)]
                            xy_weight = sum(updates) / len(updates)

                        # else decay edge
                        else:

                            xy_weight = max(z['default_ttt'], (z['ttt'] * self.__decay_factor))

                        xy_ttt = (self.__smoothing_factor * xy_weight) + ((1 - self.__smoothing_factor) * z['ttt'])
                        arc_weight += xy_ttt

                    if e['ttt'] != arc_weight:
                        print('edge %s->%s %s->%s' % (u, v, e['ttt'], arc_weight))

                    e['ttt'] = arc_weight
                    e['real_ttt'] = arc_weight

            # # reset the contraction priority queue
            # self._node_priority_pq = PriorityQueue()

            # enqueue all affected nodes for contraction
            for n, d in self.G.nodes(data = True):

                #if d['priority'] >= threshold:
                d['priority'] = sys.maxsize

            # repair the graph
            self.order_nodes()
            self.contract_graph()
            self.set_flags()

    #@profile
    def contract_graph(self, initialize=True):

        timer = Timer(__name__)
        timer.start('Contracting graph...')

        count = 0

        while True:

            try:
                v_priority, v = self._node_priority_pq.pop()
            except KeyError as e:
                break

            # lazy updates
            # new_priority = self._calc_node_priority(v)
            # if new_priority > self._node_priority_pq.min_val():
            #     print('waste')
            #     self._node_priority_pq.push(new_priority, v)
            #     continue

            if initialize:
                self.G.node[v]['priority'] = count
                v_priority = count

            #print('%s: %s nodes left' % (v, self.G.number_of_nodes() - count))

            if count % 100 == 0:
                self.__log.debug('%.4f%%' % ((count / self.num_nodes) * 100))

            #if count % 1000 == 0:
                #self.re_order_nodes()

            neighbors = set()
            count += 1

            for u, u_edge in self._predecessors(v, initialize):

                neighbors.add(u)
                w_nodes = []
                uvw_costs = []

                for w, w_edge in self._successors(v, initialize):

                    if u == w:
                        continue

                    neighbors.add(w)
                    w_nodes.append(w)
                    uvw_costs.append(u_edge[self.__weight_label] + w_edge[self.__weight_label])

                # if there are successors (which make a complete uvw path)
                if w_nodes:

                    # local search to get which paths need shortcuts
                    _, ends = self._local_search(u, v, w_nodes, uvw_costs, initialize)

                    # for each path add a shortcut
                    for end in ends:

                        weight = u_edge[self.__weight_label] + self.G[v][end][self.__weight_label]

                        tags = {
                            self.__weight_label: weight,
                            'is_shortcut': True,
                            'repl_node': v,
                        }

                        self.G.add_edge(u, end, **tags)

            if initialize:

                #print('%s neighbors to update' % (len(neighbors)))

                for n in neighbors:

                    self.G.node[n]['adj_count'] += 1
                    new_priority = self._calc_node_priority(n, initialize)
                    self._node_priority_pq.push(new_priority, n)

            #print('node: %d, inspecting %d' % (v, v_ct))

        # print('\r%.4f%%' % 100)
        self.__log.info('Nodes: %s Edges: %s' % ('{:,}'.format(self.G.number_of_nodes()), '{:,}'.format(self.G.number_of_edges())))
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
