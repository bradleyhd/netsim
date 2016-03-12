import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import json, argparse
from networkx.readwrite import json_graph as imports

parser = argparse.ArgumentParser(description='Draws a graph in 3d.')
parser.add_argument('graph_file', help='the name of the graph file')
parser.add_argument('--saveas', help='the name of the output file')

args = parser.parse_args()

config = {}
with open('config.json', 'r') as file:
    config = json.load(file)

with open('data/' + args.graph_file + '.graph', 'r') as file:
      
    data = json.load(file)
    graph = imports.node_link_graph(data)

def draw_3d(G):

    print('Drawing graph...')

    nodes = []
    colors = []
    positions = []
    xs = []
    ys = []
    zs = []
    priorities = {}
    p = []

    fig = plt.figure()
    ax = fig.gca(projection='3d')

    # plot edges
    for node_1, node_2, data in G.edges(data = True):

        # if 'real_arc' in data:
        #     #continue

        x_1 = G.node[node_1]['lon']
        y_1 = G.node[node_1]['lat']
        x_2 = G.node[node_2]['lon']
        y_2 = G.node[node_2]['lat']
        z_1 = G.node[node_1]['priority']
        z_2 = G.node[node_2]['priority']
        # z_1 = 1
        # z_2 = 1

        color = 'b'
        if data['is_shortcut']:
            color = 'r'

            # if data['highway'] in ['motorway', 'motorway_link', 'trunk', 'trunk_link', 'primary', 'primary_link']:
            #     z_1 = 10
            #     z_2 = 10
            #     color = 'g'

            # elif data['highway'] in ['secondary', 'secondary_link', 'tertiary', 'tertiary_link', 'road']:
            #     z_1 = 5
            #     z_2 = 5
            #     color = 'y'
            # else:
            #     z_1 = 0
            #     z_2 = 0
            #     color = 'r'

        # xs.extend([x_1, x_2])
        # ys.extend([y_1, y_2])
        # zs.extend([z_1, z_2])
        # colors.append(color)

        ax.plot([x_1, x_2], [y_1, y_2], [z_1, z_2], color = color)

    # ax.plot(xs, ys, zs=zs, color='r')
    plt.show()
    #plt.savefig('test.pdf')

draw_3d(graph)