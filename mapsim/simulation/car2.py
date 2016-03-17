import math, datetime, random, requests, json
import numpy as np
from mapserver.util.geo import estimate_location
from mapsim.simulation.signal import Signal

class Car(object):

    #@profile
    def __init__(self, id, sim, delay, trip):

        self.sim = sim
        self.graph = sim.graph
        
        self.id = id
        self.delay = delay
        self.trip = trip

        if self.trip:
            self.start_node = trip[0][0]
            self.end_node = trip[-1][1]

        self.current_speed = 0
        self.target_speed_adjustment = np.random.normal(0, self.sim._config['speed_stdev_m/s'])
        self.actual_trip = []
        self.leg = -1
        self.cell = -1

        self.history = []        

    def __route(self, start, end):

        if self.sim.adaptive:
            res = requests.get('http://localhost:5000/adaptive/route/%d/%d' % (start, end))
        else:
            res = requests.get('http://localhost:5000/route/%d/%d' % (start, end))
        route = res.json()
        
        return route

    def __report(self, start, end, duration):

        res = requests.get('http://localhost:5000/adaptive/report/%d/%d/%f' % (start, end, duration))

    def __look(self, leg, cell, distance):

        clear = 0
        count = 0

        for x, y in self.trip[leg::]:

            if count == 0:
                buckets = self.sim.buckets[x][y]['buckets'][cell::]
            else:
                buckets = self.sim.buckets[x][y]['buckets']

            count += 1

            #print('%s->%s: %s' % (x, y, buckets))

            for bucket in buckets:
                if bucket > 0:
                    return clear
                else:
                    clear += 1
                    if clear > distance:
                        return clear

        return clear

    def log_location(self):

        if self.leg != -1 and self.cell != -1:

            (x, y) = self.trip[self.leg]
            arc = self.sim.buckets[x][y]

            abs_time = self.sim.setup_time + datetime.timedelta(seconds=self.sim.env.now)
            (lon, lat) = arc['bucket_locations'][self.cell]
            entry = (lon, lat, abs_time.isoformat())
            self.history.append(entry)

    def run(self):

        if len(self.trip) == 0:
            return

        # wait to start
        yield self.sim.env.timeout(self.delay)

        from_leg = -1
        from_cell = -1
        to_leg = 0
        to_cell = 0

        distance = self.sim._config['cell_length_m']
        acceleration = self.sim._config['acceleration_m/s^2']

        i = 0
        while True:

            # print('----------')
            # print('Car %s attempting %s:%s->%s:%s' % (self.id, from_leg, from_cell, to_leg, to_cell))

            (from_x, from_y) = self.trip[from_leg]
            from_arc = self.sim.buckets[from_x][from_y]

            # car has reached end of route
            if to_leg >= len(self.trip):

                # decrement the cell it came from
                from_arc['buckets'][from_cell] -= 1;

                # reset
                self.cell = -1
                self.leg = -1

                # exit
                return

            # get the set of cells we're driving towards
            (to_x, to_y) = self.trip[to_leg]
            to_arc = self.sim.buckets[to_x][to_y]

            # if the target cell is actually on the next leg of the trip
            if to_cell >= len(to_arc['buckets']):

                # pick the next leg, and start over
                to_leg += 1
                to_cell = 0
                continue

            # calculate the desired headway
            target_headway = int(self.current_speed / 5)

            # look ahead to determine the actual headway
            headway = self.__look(to_leg, to_cell, target_headway)

            # print('Current speed: %s' % self.current_speed)
            # print('Target Headway: %s' % target_headway)
            # print('Headway: %s' % (headway))

            # if there's more headway than needed
            if headway > target_headway:

                # calcuate the driver's desired speed
                ffs = from_arc['ffs']
                target_speed = ffs + self.target_speed_adjustment

                # vf = sqrt(vi^2 + 2ax)
                final_speed = np.sqrt((self.current_speed ** 2) + (2 * acceleration * distance))

                # if car reaches target speed this segment
                if final_speed >= target_speed:

                    # print('Reached Target Speed')

                    # solve for distance at which it hits top speed
                    x = (target_speed ** 2 - self.current_speed ** 2)/(2 * acceleration)

                    # solve for time to reach this speed
                    t = (2 * x) / (self.current_speed + target_speed)

                    # add time at linear speed for rest of distance
                    y = distance - x
                    t += y / target_speed

                    final_speed = target_speed

                # else car accelerates for this entire cell
                else:

                    # print('Accelerating Speed')

                    # solve for time to reach this speed
                    t = (2 * distance) / (self.current_speed + final_speed)

                # prepare to sleep until the end of this cell
                self.current_speed = final_speed

                # adjust the cells
                if from_leg != -1:
                    from_arc['buckets'][from_cell] -= 1;
                to_arc['buckets'][to_cell] += 1;

                # update positions
                from_leg = to_leg
                from_cell = to_cell
                self.leg = to_leg
                self.cell = to_cell

                # increment target cell
                to_cell += 1

                # sleep for duration of the drive
                # print('Final Speed: %s' % final_speed)
                # print('Drive %ss' % t)
                yield self.sim.env.timeout(t)

            elif headway == 0:

                # if there's no headway, re-evaluate in a bit
                if headway == 0:
                    yield self.sim.env.timeout(self.sim._config['driver_reaction_time_s'])
                    continue

            elif headway == target_headway:

                # print('Maintaining Speed')
                t = distance / self.current_speed

                # prepare to sleep until the end of this cell
                # adjust the cells
                if from_leg != -1:
                    from_arc['buckets'][from_cell] -= 1;
                to_arc['buckets'][to_cell] += 1;

                # update positions
                from_leg = to_leg
                from_cell = to_cell
                self.leg = to_leg
                self.cell = to_cell

                # increment target cell
                to_cell += 1

                # sleep for duration of the drive
                # print('Final Speed: %s' % final_speed)
                # print('Drive %ss' % t)
                yield self.sim.env.timeout(t)

            # there's not enough headway, decelerate and move anyway
            else:

                # print('Decelerating')

                # linear
                #final_speed = self.current_speed - (self.current_speed / target_headway)

                # logarithmic braking function
                c = self.current_speed / np.log(target_headway)
                final_speed = c * np.log(headway)

                # (vf^2-v^2)/(2x)=a
                deceleration = (final_speed ** 2 - self.current_speed ** 2)/(2 * distance)

                # t = (vf - v)/a
                t = (final_speed - self.current_speed) / deceleration

                # prepare to sleep until the end of this cell
                self.current_speed = final_speed

                # adjust the cells
                if from_leg != -1:
                    from_arc['buckets'][from_cell] -= 1;
                to_arc['buckets'][to_cell] += 1;

                # update positions
                from_leg = to_leg
                from_cell = to_cell
                self.leg = to_leg
                self.cell = to_cell

                # increment target cell
                to_cell += 1

                # sleep for duration of the drive
                # print('Final Speed: %s' % final_speed)
                # print('Drive %ss' % t)
                yield self.sim.env.timeout(t)

