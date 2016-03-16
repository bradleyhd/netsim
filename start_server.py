import argparse, json, logging
from flask import Flask
from mapserver.routing.server import Server

app = Flask(__name__)

server = None

@app.route('/')
def hello_world():
  return 'Hello World!'

@app.route('/routes/generate/<n>')
def generate(n):
  return json.dumps(server.generate(int(n)))

@app.route('/route/<start>/<end>')
def route(start, end):
  return json.dumps(server.route(int(start), int(end), False))

@app.route('/stats')
def stats():
  return json.dumps(server._stats_data);

@app.route('/adaptive/route/<start>/<end>')
def adaptive_route(start, end):
  return json.dumps(server.route(int(start), int(end), True))

@app.route('/adaptive/report/<start>/<end>/<duration>')
@app.route('/adaptive/report/<start>/<end>/<duration>/<update>')
def report(start, end, duration, update=None):

  if update:
    return json.dumps(server.report(int(start), int(end), float(duration), int(update)))

  return json.dumps(server.report(int(start), int(end), float(duration)))

if __name__ == '__main__':

  parser = argparse.ArgumentParser(description='Launches the mapping server.')
  parser.add_argument('graph_file', help='The filename of the graph to use.')
  args = parser.parse_args()

  config = {}
  with open('config.json', 'r') as file:
      config = json.load(file)
      
      if config['decision_graph']:
        config['graph_file'] = 'data/%s.decision.graph' % args.graph_file
        config['sim_file'] = 'data/%s.sim' % args.graph_file
      else:
        config['graph_file'] = 'data/%s.graph' % args.graph_file

      server = Server(config)

  app.run(threaded=True, debug=True)
  #app.run(debug=True)