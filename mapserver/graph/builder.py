import logging, datetime, sys
import xml.parsers.expat
import networkx as nx
import itertools
from geopy.distance import great_circle
from mapserver.util.geo import estimate_location
from networkx.readwrite import json_graph
from mapserver.util.timer import Timer

class GraphBuilder(object):

    __tags_to_copy = ['name', 'oneway', 'lanes', 'highway']

    def __init__(self, config, tier=None):

        self.__log = logging.getLogger(__name__)

        self.__config = config;
        self._road_parameters = config['road_parameters'];
        self._road_segment_length_km = config['road_segment_length_km']
        self._default_node_attrs = config['default_node_attrs'];
        self._default_node_attrs['priority'] = sys.maxsize
        self._default_edge_attrs = config['default_edge_attrs'];

        self.__nodes_counter = itertools.count()
        self.__nodes_seen = {}
        self.__current_item = None

        self.__tier = tier
        self.__tiers = {
            1: ['motorway', 'motorway_link', 'trunk', 'trunk_link', 'primary', 'primary_link'],
            2: ['secondary', 'secondary_link', 'tertiary', 'tertiary_link', 'road'],
            3: ['residential']
        }

        self.graph = nx.DiGraph()

    def __start_element_handler(self, name, attrs):
        '''handles a new XML element'''

        # if it's a node
        if name == 'node':

            # generate a sequential id
            id = next(self.__nodes_counter)

            # create node object
            n = Node(attrs['id'], attrs['id'], float(attrs['lon']), float(attrs['lat']), default_attrs = self._default_node_attrs.copy())

            # record it as the current item
            self.__current_item = n

            # add the node to a dict of seen nodes
            self.__nodes_seen[attrs['id']] = n

        # if it's a way
        elif name == 'way':

            # create way object
            w = Way(attrs['id'], default_attrs = self._default_edge_attrs.copy())

            # record it as the current item
            self.__current_item = w

        # if it's a node along a waypath
        elif isinstance(self.__current_item, Way) and name == 'nd':

            # look up the node id
            n = self.__nodes_seen[attrs['ref']]

            # append the node to the current path
            self.__current_item.path.append(n.attrs['id'])

        # if it's a tag for a way
        elif name == 'tag':

            if isinstance(self.__current_item, Node):

                # if the node is an intersection with a traffic light
                if attrs['k'] == 'highway' and attrs['v'] == 'traffic_signals':

                    self.__current_item.add_prop('traffic_signal', True)

            elif isinstance(self.__current_item, Way):

                # if it's a road and a type of road we want
                if attrs['k'] == 'highway' and attrs['v'] in self._road_parameters.keys():

                    # copy the tag
                    self.__current_item.add_prop(attrs['k'], attrs['v'])

                # else if it's a tag of interest
                elif attrs['k'] in self.__tags_to_copy:

                    # copy it
                    self.__current_item.add_prop(attrs['k'], attrs['v'])

    def __end_element_handler(self, name):
        '''handles the end of an XML element'''

        if name == 'node' and isinstance(self.__current_item, Node):

            # add the node
            self.graph.add_node(self.__current_item.attrs['id'], **self.__current_item.attrs)

        # if it's the end of a way and if it's a road
        elif name == 'way' and isinstance(self.__current_item, Way) and 'highway' in self.__current_item.attrs:

            # if a tier is chosen and way is in the correct tier
            # or if no tier is chosen and way is in the list of all road types
            if (self.__tier is not None and self.__current_item.attrs['highway'] in self.__tiers[self.__tier]) or (self.__tier is None and self.__current_item.attrs['highway'] in self._road_parameters):
                props = self.__current_item.attrs

                # figure out if we should add a reversed path
                is_oneway = False
                is_motorway = (props['highway'] == 'motorway')
                is_roundabout = (props.get('junction', None) == 'roundabout')
                oneway = (props.get('oneway', None))

                if (is_motorway or is_roundabout or oneway == 'yes' or oneway == '-1') and oneway != 'no':
                    is_oneway = True

                # zip the list of nodes (path) to produce consecutive edges
                # append the path edge by edge for individual TTT estimates
                nx_path = self.__current_item.path
                for n1, n2 in zip(nx_path, nx_path[1:]):

                    # calculate the time to traverse
                    self.__calc_ttt(n1, n2, props)

                    # ensure that the edge isn't a self-loop
                    if n1 == n2:
                        self.__log.warn('Detected self-referential path edge %s->%s, skipping' % (n1, n2))
                        continue

                    # add forward path
                    self.graph.add_edge(n1, n2, **props)

                    if not is_oneway:

                        # add reversed path
                        self.graph.add_edge(n2, n1, **props)

    def __calc_ttt(self, n1, n2, edge_tags):
        '''calculates the time to traverse (TTT) an edge of the graph in millisconds'''

        # retrieve node data
        start_node = self.graph.node[n1]
        end_node = self.graph.node[n2]

        # extract coordinates into tuples
        # geopy accepts tupes in (lat, long format)
        start_coord = (start_node['lat'], start_node['lon'])
        end_coord = (end_node['lat'], end_node['lon'])

        # calculate distance with geopy
        # vincenty is good, but slow, and has convergence problems
        # great circle is a lot faster and accurate enough (for now)
        dist_km = great_circle(start_coord, end_coord).kilometers
        edge_tags['length'] = dist_km

        # assume speeds based on highway classification
        ffs = self._road_parameters[edge_tags['highway']]['ffs_kph']
        edge_tags['ffs'] = ffs

        # calculate estimated time to traverse in milliseconds
        # millisecond resolution means many more steps for simulations,
        # but also mean that rounding errors are only made here and not
        # inside of a bidirectional dijkstra algorithm
        ttt = int((dist_km / ffs) * 60 * 60 * 1000)

        edge_tags['ttt'] = ttt
        edge_tags['real_ttt'] = ttt
        edge_tags['default_ttt'] = ttt

    def from_file(self, filepath, decision_graph=False):

        timer = Timer(__name__)
        timer.start('Building graph from \'%s\'...' % (filepath))

        p = xml.parsers.expat.ParserCreate()
        p.StartElementHandler = self.__start_element_handler
        p.EndElementHandler = self.__end_element_handler

        p.ParseFile(open(filepath, 'rb'))

        if decision_graph:

            self.decision_graph = self.__decision_graph()

            # remove orphan nodes
            solitary = [n for n, d in self.decision_graph.degree_iter() if d == 0]
            self.decision_graph.remove_nodes_from(solitary)

            timer.stop()
            self.__log.info('Graph successfully built')
            self.__log.info('Nodes: %s Edges: %s' % ('{:,}'.format(self.decision_graph.number_of_nodes()), '{:,}'.format(self.decision_graph.number_of_edges())))

            return self.decision_graph

        else:

            # remove orphan nodes
            solitary = [n for n, d in self.graph.degree_iter() if d == 0]
            self.graph.remove_nodes_from(solitary)

            # find decision nodes
            self.__find_decision_nodes()

            timer.stop()

            self.__log.info('Graph successfully built')
            self.__log.info('Nodes: %s Edges: %s' % ('{:,}'.format(self.graph.number_of_nodes()), '{:,}'.format(self.graph.number_of_edges())))

            return self.graph

    def __find_decision_nodes(self):
        '''marks nodes as decision nodes'''

        timer = Timer(__name__)
        timer.start('Computing decision nodes...')

        count = 0

        # for each node
        for n, data in self.graph.nodes(data = True):

            # create a list of all way_ids that are successors of this node
            ways = [e['osm_way_id'] for e in self.graph.succ[n].values()]

            # if there are more than one successor to a node,
            # and if there is more than one osm_way_id, then it is a decision node
            if len(self.graph.succ[n]) > 1 and len(set(ways)) > 1:
                data['decision_node'] = True
                count += 1

        self.__log.info('Decision nodes: %s' % (count))
        timer.stop()

    def __decision_graph(self):

        timer = Timer(__name__)
        timer.start('Computing decision graph...')

        G = self.graph.copy()
        self.decision_map = {}
        self.__recurse_map = {}

        # for each node
        for v in G.nodes_iter():

            # create a list of all way_ids that are incident to this node
            ways = []
            ways.extend([e['osm_way_id'] for e in G.succ[v].values()])
            ways.extend([e['osm_way_id'] for e in G.pred[v].values()])

            predecessors = [(pred, edge) for pred, edge in G.pred[v].items()]
            successors = [(succ, edge) for succ, edge in G.succ[v].items()]

            # if there are at least 2 predecessors and 2 successors
            # and if there is only 1 distinct way_id, remove the node
            if len(G.pred[v]) == 2 and len(G.succ[v]) == 2 and len(set(ways)) < 2:

                for (u, u_edge), (w, w_edge) in itertools.product(predecessors, successors):

                    if u == w:
                        continue

                    if u_edge['osm_way_id'] == w_edge['osm_way_id']:
                        tags = u_edge.copy()
                        ttt = u_edge['ttt'] + w_edge['ttt']
                        tags['ttt'] = ttt
                        tags['real_ttt'] = ttt
                        tags['default_ttt'] = ttt

                        G.remove_edge(u, v)
                        G.remove_edge(v, w)

                        if (u, w) in self.__recurse_map and self.__recurse_map[(u, w)][1] < ttt:
                            continue
                        elif w in self.graph[u] and self.graph[u][w]['ttt'] < ttt:
                            continue

                        G.add_edge(u, w, **tags)
                        self.__recurse_map[(u, w)] = (v, ttt)
                        

            # if there is exactly 1 predecessor and 1 successor
            elif len(G.pred[v]) == 1 and len(G.succ[v]) == 1:

                # if the road is for sure a oneway:
                u, u_edge = list(G.pred[v].items())[0]
                w, w_edge = list(G.succ[v].items())[0]

                if u == w:
                    continue

                if 'oneway' in u_edge and 'oneway' in w_edge and u_edge['osm_way_id'] == w_edge['osm_way_id']:

                    tags = u_edge.copy()
                    ttt = u_edge['ttt'] + w_edge['ttt']
                    tags['ttt'] = ttt
                    tags['real_ttt'] = ttt
                    tags['default_ttt'] = ttt

                    G.remove_edge(u, v)
                    G.remove_edge(v, w)

                    if (u, w) in self.__recurse_map and self.__recurse_map[(u, w)][1] < ttt:
                            continue
                    elif w in self.graph[u] and self.graph[u][w]['ttt'] < ttt:
                        continue

                    G.add_edge(u, w, **tags)
                    self.__recurse_map[(u, w)] = (v, ttt)
                    

        self.__log.info('Nodes: %s Edges: %s' % ('{:,}'.format(G.number_of_nodes()), '{:,}'.format(G.number_of_edges())))

        for x, y, e in G.edges(data=True):

            # if this is an original edge, then only add it to the decision map if the
            # collapsed route is shorter than the original

            # if y in self.graph[x] and (x, y) in self.__recurse_map and self.graph[x][y]['ttt'] < self.__recurse_map[(x, y)][1]:
            #     print('continued %s->%s %s < %s' % (x, y, self.graph[x][y]['ttt'], self.__recurse_map[(x, y)][1]))
            #     continue

            route = self.__uncontract_forwards(x, y)
            self.decision_map[(x, y)] = route

        timer.stop()

        return G

    def __uncontract_forwards(self, u, w):

        # if there is a contracted node, recursively search for more contracted nodes
        if (u, w) in self.__recurse_map:
            v = self.__recurse_map[(u, w)][0]
            return self.__uncontract_forwards(u, v) + self.__uncontract_forwards(v, w)

        return [(u, w)]

    def __compute_segments(self):
        '''divide each road into discrete segments'''

        timer = Timer(__name__)
        timer.start('Quantizing road segments...')

        segments = {}

        for x, y, e in self.graph.edges(data = True):

            start_node = self.graph.node[x]
            end_node = self.graph.node[y]

            dist_km = e['length']
            num_buckets = int(dist_km / self._road_segment_length_km)
            num_lanes = self._road_parameters[e['highway']]['lanes']

            if x not in segments:
                segments[x] = {}

            segments[x][y] = {
              'buckets': [0] * num_buckets,
              'num_buckets': num_buckets,
              'ffs': e['ffs'],
              'bucket_capacity': num_lanes,
              'bucket_locations': [None] * num_buckets
            }

            for i in range(0, num_buckets):
                (lon, lat) = estimate_location(
                    end_node['lon'], end_node['lat'],
                    start_node['lon'], start_node['lat'],
                    (i * self._road_segment_length_km) + self._road_segment_length_km / 2)
                segments[x][y]['bucket_locations'][i] = (lon, lat)

        timer.stop()

        return segments

    def get_sim_data(self, decision_graph=False):

        sim_data = {
            'segments': self.__compute_segments()
        }

        if decision_graph:
            sim_data['decision_route_map'] = self.decision_map

        return sim_data

class Way:

    def __init__(self, osm_way_id, default_attrs={}):

        self.attrs = {
            'osm_way_id': osm_way_id,
        }

        self.attrs.update(default_attrs)

        self.path = []

    def add_prop(self, k, v):

        self.attrs[k] = v

class Node:

    def __init__(self, id, osm_id, lon, lat, default_attrs={}):

        self.attrs = {
            'id': id,
            'osm_id': osm_id,
            'lon': lon,
            'lat': lat,
        }

        self.attrs.update(default_attrs)

    def add_prop(self, k, v):

        self.attrs[k] = v
