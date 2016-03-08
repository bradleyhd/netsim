import networkx as nx
import argparse, json, random

from mapserver.graph.builder import GraphBuilder
from mapserver.graph.contractor import GraphContractor
from networkx.readwrite import json_graph
from mapserver.routing.router import Router


parser = argparse.ArgumentParser(description='Constructs and contracts a graph.')
parser.add_argument('data_file', help='the name of the data file')
parser.add_argument('trips', help='number of routes to check')
parser.add_argument('--saveas', help='the name of the output file')

args = parser.parse_args()

config = {}
with open('config.json', 'r') as file:
    config = json.load(file)

data_file_path = 'data/%s.osm' % args.data_file

# build the graph
factory = GraphBuilder(config)
G = factory.from_file(data_file_path)

H = G.copy()

# contract the graph
C = GraphContractor(config, G)
C.order_nodes()
C.contract_graph()
C.set_flags()

router = Router(G)

count = 0
paths=[]

for x in range(0, int(args.trips)):
    (start_node, end_node) = random.sample(list(G.nodes()), 2)
    # start_node = 1827
    # end_node = 1914
    # start_node = 322
    # end_node = 684
    print('---')
    print('Finding path from', start_node, 'to', end_node)

    try:
        check_path = nx.shortest_path(H,source = start_node,target = end_node, weight='ttt')
        check_path = list(zip(check_path, check_path[1:]))
    except:
        check_path = []

    path = router.route(start_node, end_node)
    # print('%s: %s' % (x, route))
    # paths.append(route)

    if path != check_path:
        count += 1
        print('Error, disagreement:')
        print(path)
        print(check_path)
        break

print('%d out of %s paths disagree' % (count, args.trips))

# draw('test.pdf')
