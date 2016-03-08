import math, datetime, random, requests, json
import numpy as np
from mapsim.util.geo import estimate_location
from mapsim.simulation.signal import Signal
# from profilehooks import profile, timecall, coverage

class NoMoreLegsException(Exception):
    pass

class NoMoreCellsException(Exception):
    pass

class Car(object):

    #@profile
    def __init__(self, id, sim, delay, start_node, end_node):

        self.sim = sim
        #self.sim.env = sim.env
        self.graph = sim.graph
        
        self.id = id
        self.start_node = start_node
        self.end_node = end_node
        self.delay = delay
        self.location_history = True

        # np.random.seed()
        self.start_node = np.random.choice(self.graph.nodes())
        self.end_node = np.random.choice(self.graph.nodes())
        # self.start_node = 1827
        # self.end_node = 1914
        self.trip = self.__route(self.start_node, self.end_node)
        #print('%s: %s' % (self.id, self.trip))
        self.original_trip = self.trip.copy()
        self.actual_trip = []
        #print('Car %s: %s->%s = %s' % (self.id, self.start_node, self.end_node, self.trip))

        # how often in ms to wake up
        self.wake_frequency = 10
        self.num_wakes = -1

        # Start the run process everytime an instance is created.
        
        self.leg = -1
        self.cell = -1

        self.driving_time = 0
        self.driving_distance = 0
        self.total_driving_time = 0
        self.total_driving_distance = 0
        self.history = []        

        self.wait = 0
        self.halt = False
        self.done = False

    #@profile
    def __route(self, start, end):

        if self.sim.adaptive:
            res = requests.get('http://localhost:5000/adaptive/route/%d/%d' % (start, end))
        else:
            res = requests.get('http://localhost:5000/route/%d/%d' % (start, end))
        route = res.json()
        
        return route

    def __report(self, start, end, duration):

        res = requests.get('http://localhost:5000/adaptive/report/%d/%d/%f' % (start, end, duration))

    #@profile
    def __can_move_to(self, from_leg, from_cell, to_leg, to_bucket):

        # if the next leg doesn't exist
        if to_leg >= len(self.trip):
            raise NoMoreLegsException()

        # get the target leg
        (x, y) = self.trip[to_leg]
        #arc = self.graph[x][y]
        arc = self.sim.buckets[x][y]

        # if the next bucket doesn't exist
        if to_bucket >= arc['num_buckets']:
            raise NoMoreCellsException()

        # if there's room in the next bucket
        room = arc['buckets'][to_bucket] < arc['bucket_capacity']

        if not room:
            return False

        # check for signals
        if to_bucket == arc['num_buckets'] - 1 and y in self.sim.signal_map:

            if not self.sim.signal_map[y].canGo(x, y):

                return False

        return True

    #@profile
    def __move_to(self, from_leg, from_cell, to_leg, to_cell):

        # decrement the previous cell if there is one
        if from_leg > -1 and from_cell > -1:
            (from_x, from_y) = self.trip[from_leg]
            #from_arc = self.graph[from_x][from_y]
            from_arc = self.sim.buckets[from_x][from_y]
            from_arc['buckets'][from_cell] -= 1;
            # print('decrementing (%d, %d)=%d' % (from_leg, from_cell, from_arc['buckets'][from_cell]))

        # increment the next cell
        (to_x, to_y) = self.trip[to_leg]
        #to_arc = self.graph[to_x][to_y]
        to_arc = self.sim.buckets[to_x][to_y]
        to_arc['buckets'][to_cell] += 1;
        # print('incrementing (%d, %d)=%d' % (to_leg, to_cell, to_arc['buckets'][to_cell]))

        # calculate the time spent driving in this cell
        # normally randomize speed by +/- 2 km/h
        ffs = to_arc['ffs']
        speed = np.random.normal(ffs, 2)
        #speed = ffs

        # if to_x == 1899 or to_x == 7041:
        #     print('slowing %s' % self.id)
        #     speed = 10

        # calculate how long to drive 5m in in milliseconds SECONDS
        duration = (0.005 / speed) * 3600 * 1000

        #battleground 1899 7041
        #print('car %s moving to %s, %s' % (self.id, to_x, to_y))

        if (to_x == 1899 and to_cell == 0):
        #if to_x in self.sim.bottlenecks and to_cell == 0:
            print('>>>>>>>>>>>>>>SLOWING %s' % self.id)
            duration = duration + 15000 #self.sim.bottlenecks[to_x]

        # log the location
        if self.location_history: self.__log_location_now(to_leg, to_cell, to_arc)

        # scale to seconds
        #duration = duration / 1000.0

        return duration

    #@profile
    def __log_location_now(self, leg, cell, arc=None):

        if leg > -1 and cell > -1:

            if arc == None:
                (x, y) = self.trip[leg]
                arc = self.sim.buckets[x][y]

            abs_time = self.sim.setup_time + datetime.timedelta(milliseconds=self.sim.env.now)
            (lon, lat) = arc['bucket_locations'][cell]
            entry = (lon, lat, abs_time.isoformat())
            self.history.append(entry)

    #@profile
    def run(self):

        if len(self.trip) == 0:
            return

        current_cell = -1
        current_leg = -1
        next_cell = 0
        next_leg = 0
        wait_count = 0
        leg_duration = -1

        #wait to start
        #wait = np.random.randint(0, self.sim_length / 4)
        yield self.sim.env.timeout(self.delay)

        while True:

            try:

                #print('car %d attempting (%d,%d)-(%d,%d)' % (self.id, current_leg, current_cell, next_leg, next_cell))
                #print('\r%s' % self.id, end='')

                # if the car can move
                if self.__can_move_to(current_leg, current_cell, next_leg, next_cell):
                    #print('yes')

                    wait_count = 0

                    # move it
                    duration = self.__move_to(current_leg, current_cell, next_leg, next_cell)
                    # print('car can move, will take %d' % duration)

                    (x, y) = self.trip[next_leg]
                    #arc = self.graph[x][y]

                    #martinsville 700 4280
                    #battleground 882 6692
                    # if x == 882 and y == 6692 and next_cell >= len(arc['buckets']) - 1:
                    #     print('stalling %s' % self.id)
                    #     print(arc['buckets'])
                    #     duration += 1000000

                    # if x == 6692 and y == 882 and next_cell >= len(arc['buckets']) - 1:
                    #     print('stalling %s' % self.id)
                    #     print(arc['buckets'])
                    #     duration += 1000000

                    yield self.sim.env.timeout(duration)
                    self.total_driving_time += duration
                    leg_duration += duration
                    current_cell = next_cell
                    current_leg = next_leg
                    next_cell += 1

                # if it can not move, wait
                else:

                    # print('car can not move, sleeping')
                    wait_count += 1

                    if self.location_history and wait_count % 5 == 0:
                        self.__log_location_now(current_leg, current_cell)

                    t = 200
                    yield self.sim.env.timeout(t)
                    self.total_driving_time += t
                    leg_duration += t

            except NoMoreLegsException as e:

                # trip is over
                # print('trip is over')

                (x, y) = self.trip[current_leg]
                #arc = self.graph[x][y]
                arc = self.sim.buckets[x][y]
                if len(arc['buckets']) > 0:
                    arc['buckets'][current_cell] -= 1;
                # print('decrementing (%d, %d)=%d' % (current_leg, current_cell, arc['buckets'][current_cell]))

                # print('---')
                # print('Car %s' % self.id)
                # print('Original Trip: %s' % self.original_trip)
                # print('Actual Trip: %s' % self.actual_trip)
                # print('Same? %s' % (self.original_trip == self.actual_trip))
                # if ((self.original_trip != self.actual_trip)):
                #     raise KeyError()

                self.done = True
                print('car %s done' % (self.id))

                return

            except NoMoreCellsException as e:

                #print('---')

                (x, y) = self.trip[next_leg]
                arc = self.graph[x][y]

                # log duration on current leg
                if self.sim.adaptive and leg_duration != -1:

                    #self.contractor.update(x, y, leg_duration)
                    #self.contractor.update(x, y, leg_duration)
                    self.__report(x, y, leg_duration)
                    #pass
                    
                self.actual_trip.append([x, y])
                leg_duration = 0

                #print('Car %s has traversed %s->%s' % (self.id, x, y))
                #print('Route so far: %s' % self.actual_trip)

                #print('New route: %s' % self.trip)

                # try again on the next leg:
                next_cell = 0
                next_leg = next_leg + 1
                # print('buckets exhausted, trying (%d, %d)' % (next_leg, next_cell))

                if next_leg < len(self.trip) and self.sim.adaptive:

                    (x, y) = self.trip[next_leg]
                    if 'decision_node' in self.graph.node[x]: 

                        # ask for an updated route from end of this leg to end node
                        
                        #new_route = self.router.route(x, self.end_node)
                        new_route = self.__route(x, self.end_node)
                        new_trip = self.actual_trip + new_route

                        if new_trip != self.trip:
                            #print(new_trip)
                            #print(self.trip)
                            print('*************** rerouting: %s' % self.id)

                        self.trip = new_trip
                        #print('New route(%s, %s): %s' % (y, self.end_node, self.trip))

                    # else:
                        #print('Old route(%s, %s): %s' % (y, self.end_node, self.trip))

                continue
