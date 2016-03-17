import math, datetime, random, requests, json
import numpy as np
from mapserver.util.geo import estimate_location
from mapsim.simulation.signal import Signal
# from profilehooks import profile, timecall, coverage

class NoMoreLegsException(Exception):
    pass

class NoMoreCellsException(Exception):
    pass

class Car(object):

    #@profile
    def __init__(self, id, sim, delay, trip):

        self.sim = sim
        self.graph = sim.graph
        
        self.id = id
        self.delay = delay
        self.location_history = True

        self.trip = trip
        if self.trip:
            self.start_node = trip[0][0]
            self.end_node = trip[-1][1]

        self.current_speed = 0
        self.target_speed_adjustment = np.random.normal(0, self.sim._config['speed_stdev_m/s'])

        #print('%s: %s' % (self.id, self.trip))
        self.original_trip = self.trip.copy()
        self.actual_trip = []
        #print('Car %s: %s->%s = %s' % (self.id, self.start_node, self.end_node, self.trip))

        self.leg = 0
        self.cell = 0

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
        if self.sim._config['signals'] and to_bucket == arc['num_buckets'] - 1 and y in self.sim.signal_map:

            if not self.sim.signal_map[y].canGo(x, y):

                return False

        return True

    #@profile
    def __move_to(self, from_leg, from_cell, to_leg, to_cell):

        space = self._look(to_leg, to_cell, 5)

        if space == 5:

            # decrement the previous cell if there is one
            if from_leg > -1 and from_cell > -1:
                (from_x, from_y) = self.trip[from_leg]
                from_arc = self.sim.buckets[from_x][from_y]
                from_arc['buckets'][from_cell] -= 1;

            # increment the next cell
            (to_x, to_y) = self.trip[to_leg]
            to_arc = self.sim.buckets[to_x][to_y]
            to_arc['buckets'][to_cell] += 1;

        else:

            to_arc = self.sim.buckets[from_x][from_y]

        # calculate the speed in m/s
        # normally randomize speed by +/- 2 m/s
        ffs = to_arc['ffs']
        target_speed = ffs + self.target_speed_adjustment
        if self.id == 1:
            target_speed = 70
        acceleration = self.sim._config['acceleration_m/s^2']
        distance = self.sim._config['cell_length_m']


        if space < 5:

            final_speed = self.current_speed - (self.current_speed / 5)

            # (vf^2-v^2)/(2x)=a
            deceleration = (final_speed ** 2 - self.current_speed ** 2)/(2 * distance)
            print('final: %s, dec: %s' % (final_speed, deceleration))

            # t = (vf - v)/a
            t = (final_speed - self.current_speed) / deceleration

        else:

            # vf = sqrt(vi^2 + 2ax)
            final_speed = np.sqrt((self.current_speed ** 2) + (2 * acceleration * distance))

            # if car reaches target speed this segment
            if final_speed >= target_speed:

                # solve for distance at which it hits top speed
                x = (target_speed ** 2 - self.current_speed ** 2)/(2 * acceleration)

                # solve for time to reach this speed
                t = (2 * x) / (self.current_speed + target_speed)

                # add time at linear speed for rest of distance
                y = distance - x
                t += y / target_speed

                final_speed = target_speed

            else:

                # solve for time to reach this speed
                t = (2 * distance) / (self.current_speed + final_speed)

        self.current_speed = final_speed

        #print(t)
        print('car %s: path ahead is: %s' % (self.id, self._look(to_leg, to_cell, 5)))

        print(t)
        return t

    def __attempt_move(self, from_leg, from_cell, to_leg, to_cell):

        print('Car %s attempting %s:%s->%s:%s' % (self.id, from_leg, from_cell, to_leg, to_cell))

        target_headway = 5
        headway = self.__look(to_leg, to_cell, target_headway)
        print('Headway: %s' % (headway))

        # if there's headway, accelerate or maintain speed
        if headway == target_headway:

            # get current cells
            (from_x, from_y) = self.trip[from_leg]
            from_arc = self.sim.buckets[from_x][from_y]

            ffs = from_arc['ffs']
            target_speed = ffs + self.target_speed_adjustment
            if self.id == 1:
                target_speed = 70
            acceleration = self.sim._config['acceleration_m/s^2']
            distance = self.sim._config['cell_length_m']

            # vf = sqrt(vi^2 + 2ax)
            final_speed = np.sqrt((self.current_speed ** 2) + (2 * acceleration * distance))

            # if car reaches target speed this segment
            if final_speed >= target_speed:

                # solve for distance at which it hits top speed
                x = (target_speed ** 2 - self.current_speed ** 2)/(2 * acceleration)

                # solve for time to reach this speed
                t = (2 * x) / (self.current_speed + target_speed)

                # add time at linear speed for rest of distance
                y = distance - x
                t += y / target_speed

                final_speed = target_speed

            else:

                # solve for time to reach this speed
                t = (2 * distance) / (self.current_speed + final_speed)

            # sleep in position
            yield self.sim.env.timeout(t)

            # car has moved, update the cells
            from_arc['buckets'][from_cell] -= 1;

            (to_x, to_y) = self.trip[to_leg]
            to_arc = self.sim.buckets[to_x][to_y]
            to_arc['buckets'][to_cell] += 1;

            # update positions
            self.current_leg = to_leg
            self.current_cell = to_cell
            self.next_cell = to_cell + 1

            if self.next_cell > len(to_arc['buckets']):
                self.next_leg += 1
                self.next_cell = 0

            if self.next_leg > len(self.trip):
                return

        # there's not enough headway
        else:

            yield self.sim.env.timeout(1)

    def __look(self, leg, cell, distance):

        clear = 0
        count = 0

        for x, y in self.trip[leg::]:

            if count == 0:
                buckets = self.sim.buckets[x][y]['buckets'][cell::]
            else:
                buckets = self.sim.buckets[x][y]['buckets']

            count += 1

            print('%s->%s: %s' % (x, y, buckets))

            for bucket in buckets:
                if bucket > 0:
                    return clear
                else:
                    clear += 1
                    if clear > distance:
                        return clear

        return clear

    #@profile
    def __log_location_now(self, leg, cell, arc=None):

        if leg > -1 and cell > -1:

            if arc == None:
                (x, y) = self.trip[leg]
                arc = self.sim.buckets[x][y]

            abs_time = self.sim.setup_time + datetime.timedelta(seconds=self.sim.env.now)
            (lon, lat) = arc['bucket_locations'][cell]
            entry = (lon, lat, abs_time.isoformat())
            self.history.append(entry)

    def log_location(self):

        # if self.leg != -1 and self.cell != -1:
        self.__log_location_now(self.leg, self.cell)

    #@profile
    def run(self):

        if len(self.trip) == 0:
            return

        #wait to start
        #wait = np.random.randint(0, self.sim_length / 4)
        #yield self.sim.env.timeout(self.delay)

        # if self.id == 1:
        #     yield self.sim.env.timeout(10)

        from_leg = -1
        from_cell = -1
        to_leg = 0
        to_cell = 0

        distance = self.sim._config['cell_length_m']
        acceleration = self.sim._config['acceleration_m/s^2']

        i = 0
        while True:

            print('----------')
            print('Car %s attempting %s:%s->%s:%s' % (self.id, from_leg, from_cell, to_leg, to_cell))

            target_headway = int(self.current_speed / 5)
            headway = self.__look(to_leg, to_cell, target_headway)
            print('Current speed: %s' % self.current_speed)
            print('Target Headway: %s' % target_headway)
            print('Headway: %s' % (headway))

            # get current cells
            (from_x, from_y) = self.trip[from_leg]
            from_arc = self.sim.buckets[from_x][from_y]

            # if there's headway, accelerate or maintain speed
            if headway > target_headway:

                ffs = from_arc['ffs']
                target_speed = ffs + self.target_speed_adjustment
                # if self.id == 1:
                #     target_speed = 40

                #acceleration = self.sim._config['acceleration_m/s^2']
                # distance = self.sim._config['cell_length_m']

                # vf = sqrt(vi^2 + 2ax)
                final_speed = np.sqrt((self.current_speed ** 2) + (2 * acceleration * distance))

                # if car reaches target speed this segment
                if final_speed >= target_speed:

                    print('Reached Target Speed')

                    # solve for distance at which it hits top speed
                    x = (target_speed ** 2 - self.current_speed ** 2)/(2 * acceleration)

                    # solve for time to reach this speed
                    t = (2 * x) / (self.current_speed + target_speed)

                    # add time at linear speed for rest of distance
                    y = distance - x
                    t += y / target_speed

                    final_speed = target_speed

                    # if self.id == 0 and self.sim.env.now >= 30:
                    #     print('doubling')
                    #     t *= 2

                else:

                    print('Accelerating Speed')
                    # solve for time to reach this speed
                    t = (2 * distance) / (self.current_speed + final_speed)

                self.current_speed = final_speed
                
                # car has moved, update the cells
                from_arc['buckets'][from_cell] -= 1;

                (to_x, to_y) = self.trip[to_leg]
                to_arc = self.sim.buckets[to_x][to_y]
                to_arc['buckets'][to_cell] += 1;

                # update positions
                from_leg = to_leg
                from_cell = to_cell

                # save position for location logging
                self.leg = to_leg
                self.cell = to_cell

                # increment cell
                to_cell += 1

                # sleep in position
                print('Final Speed: %s' % final_speed)
                print('Drive %ss' % t)
                yield self.sim.env.timeout(t)

                if to_cell >= len(to_arc['buckets']):
                    to_leg += 1
                    to_cell = 0

                if to_leg > len(self.trip):
                    return

            elif headway == target_headway:

                if self.current_speed == 0 or headway == 0:
                    yield self.sim.env.timeout(0.2)
                    continue

                print('Maintaining Speed')
                t = distance / self.current_speed

                # car has moved, update the cells
                from_arc['buckets'][from_cell] -= 1;

                (to_x, to_y) = self.trip[to_leg]
                to_arc = self.sim.buckets[to_x][to_y]
                to_arc['buckets'][to_cell] += 1;

                # update positions
                from_leg = to_leg
                from_cell = to_cell

                # save position for location logging
                self.leg = to_leg
                self.cell = to_cell

                # increment cell
                to_cell += 1

                print('Drive %ss' % t)

                yield self.sim.env.timeout(t)

                if to_cell >= len(to_arc['buckets']):
                    to_leg += 1
                    to_cell = 0

                if to_leg > len(self.trip):
                    return

            # there's not enough headway, decelerate and move anyway
            else:

                if self.current_speed == 0 or headway == 0:
                    yield self.sim.env.timeout(0.2)
                    continue

                print('Decelerating')

                # linear
                #final_speed = self.current_speed - (self.current_speed / target_headway)

                # logarithmic

                c = self.current_speed / np.log(target_headway)
                #print('fn: %s * ln(%s) = %s' % (c, headway, c * np.log(headway)))

                # while headway >= 0:
                #     print('fn: %s * ln(%s) = %s' % (c, headway, c * np.log(headway)))
                #     headway -= 1

                final_speed = c * np.log(headway)

                # (vf^2-v^2)/(2x)=a
                deceleration = (final_speed ** 2 - self.current_speed ** 2)/(2 * distance)

                # t = (vf - v)/a
                t = (final_speed - self.current_speed) / deceleration

                self.current_speed = final_speed

                print('Final Speed: %s' % final_speed)
                print('Drive %ss' % t)

                # car has moved, update the cells
                from_arc['buckets'][from_cell] -= 1;

                (to_x, to_y) = self.trip[to_leg]
                to_arc = self.sim.buckets[to_x][to_y]
                to_arc['buckets'][to_cell] += 1;

                # update positions
                from_leg = to_leg
                from_cell = to_cell

                # save position for location logging
                self.leg = to_leg
                self.cell = to_cell

                # increment cell
                to_cell += 1

                yield self.sim.env.timeout(t)

                if to_cell >= len(to_arc['buckets']):
                    to_leg += 1
                    to_cell = 0

                if to_leg > len(self.trip):
                    return



