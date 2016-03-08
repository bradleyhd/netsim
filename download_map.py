import argparse
import os.path

from mapserver.graph.downloader import MapDownloader

parser = argparse.ArgumentParser(description='Downloads OpenStreetMap data.')
parser.add_argument('top', type=float)
parser.add_argument('left', type=float)
parser.add_argument('bottom', type=float)
parser.add_argument('right', type=float)
parser.add_argument('--saveas', help='the name of the output file')

args = parser.parse_args()

downloader = MapDownloader()

file_name = args.saveas + '.osm' if args.saveas else 'data.osm'
file_path = os.path.dirname(os.path.realpath(__file__)) + '/data/' + file_name

downloader.to_file(args.top, args.left, args.bottom, args.right, file_path = file_path)
