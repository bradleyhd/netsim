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

        self.order = -1

        self.delay = delay
        self.trip = trip
        self.actual_trip = []

        if self.trip:
            self.start_node = trip[0][0]
            self.end_node = trip[-1][1]

        self.current_speed = 0

        # set variation in target speed aka "speeders"
        if self.sim._config['speed_stdev_m/s'] > 0:
            np.random.seed()
            self.target_speed_adjustment = np.random.normal(0, self.sim._config['speed_stdev_m/s'])
        else:
            self.target_speed_adjustment = 0

        # set variation in acceleration by car/driver combo
        if self.sim._config['acceleration_stdev_m/s^2'] > 0:
            self.acceleration_adjustment = np.random.normal(0, self.sim._config['acceleration_stdev_m/s^2'])
        else:
            self.acceleration_adjustment = 0

        self.leg = -1
        self.cell = -1

        self.report_queue = []
        self.needs_reroute = False
        self.history = [] 
        self.total_driving_time = 0  
        self.done = False
        self.decision_count = 0

    def reset(self):

        self.decision_count = 0
        self.needs_reroute = False
        self.actual_trip = []
        self.current_speed = 0
        self.leg = -1
        self.cell = -1
        self.history = [] 
        self.total_driving_time = 0  
        self.done = False

    def __route(self, start, end):

        # res = requests.get('%s/route/%d/%d' % (self.sim._config['routing_server_url'], start, end))
        # route = res.json()
        route = self.sim.server.route(start, end)
        
        return route

    # def send_reports(self):
    #     while len(self.report_queue):
    #         start, end, duration = self.report_queue.pop()
    #         res = requests.get('%s/report/%d/%d/%f' % (self.sim._config['routing_server_url'], start, end, duration))

    def __report(self, start, end, duration):

        # pass
        # self.report_queue.append((start, end, duration))
        # res = requests.get('%s/report/%d/%d/%f' % (self.sim._config['routing_server_url'], start, end, duration))
        self.sim.server.report(start, end, duration)

    def _send_reports(self):
        for start, end, duration in self.report_queue:
            self.sim.server.report(start, end, duration)

    #@profile
    def __look(self, leg, cell, distance):

        clear = 0
        # count = 0
        # trip = self.trip
        # sim = self.sim

        for x, y in self.trip[leg::]:

            # if count == 0:
            # buckets = self.sim.buckets[x][y]['buckets'][cell::]
            # else:
            #     buckets = self.sim.buckets[x][y]['buckets']

            # count += 1

            #print('%s->%s: %s' % (x, y, buckets))

            for bucket in self.sim.buckets[x][y]['buckets'][cell::]:

                # print(clear, distance)
                if bucket != 0 or clear >= distance:
                    return clear

                clear += 1

                # if bucket == 0:
                #     if clear >= distance:
                #         return clear
                #     else:
                #         clear += 1
                # else:
                #     return clear       

            cell = 0

        return clear

    def log_location(self):

        if self.leg != -1 and self.cell != -1:

            (x, y) = self.trip[self.leg]
            arc = self.sim.buckets[x][y]

            abs_time = self.sim.setup_time + datetime.timedelta(seconds=self.sim.env.now)
            (lon, lat) = arc['bucket_locations'][self.cell]
            entry = (lon, lat, abs_time.isoformat())
            self.history.append(entry)

    # def reroute(self):

    #     (x, y) = self.trip[self.leg]

    #     # print('reroute car %s on %s->%s' % (self.id, x, y))
    #     # print(self.leg)

        
    #     # print('old route:   %s' % self.trip)
    #     # print('Trip so far: %s' % self.actual_trip)
        
    #     # print('decision_node' in self.sim.graph.node[y])

    #     new_route = self.__route(y, self.end_node)

    #     # print('new route    %s' % new_route)

        
        
        
    #     new_trip = self.actual_trip + new_route

    #     # if new_trip != self.trip:
            
    #     #     print(new_trip)
    #     #     print(self.trip)
    #     #     print('*************** rerouting: %s' % self.id)

    #     self.trip = new_trip
    #     self.needs_reroute = False

    #@profile
    def run(self):

        if len(self.trip) == 0:
            return

        # wait to start
        #if self.id > 0:
        # yield self.sim.env.timeout(self.delay)

        self.order = self.sim.orderer
        self.sim.orderer += 1

        from_leg = -1
        from_cell = -1
        to_leg = 0
        to_cell = 0

        leg_duration = 0

        distance = self.sim._config['cell_length_m']
        acceleration = self.sim._config['acceleration_m/s^2'] + self.acceleration_adjustment
        decision_count = 0

        i = 0
        while True:

            # print('---')
            # print('Hello from Car %s' % self.id)
            # print('Time is now %s' % self.sim.env.now)

            # if self.needs_reroute:
            #     yield self.env.timeout(self.sim._config['driver_reaction_time_s'])

            # print('----------')
            # print('Car %s attempting %s:%s->%s:%s' % (self.id, from_leg, from_cell, to_leg, to_cell))

            # (from_x, from_y) = self.trip[from_leg]
            from_arc = self.sim.buckets[self.trip[from_leg][0]][self.trip[from_leg][1]]

            # car has reached end of route
            if to_leg >= len(self.trip):

                # decrement the cell it came from
                from_arc['buckets'][from_cell] -= 1;

                # reset
                self.cell = -1
                self.leg = -1

                self.done = True
                print('Car %s done' % self.id)

                # exit
                return

            # get the set of cells we're driving towards
            # (to_x, to_y) = self.trip[to_leg]
            to_arc = self.sim.buckets[self.trip[to_leg][0]][self.trip[to_leg][1]]

            # if the target cell is actually on the next leg of the trip
            if to_cell >= len(to_arc['buckets']):

                # ask for a new route on this leg
                if self.sim._config['adaptive_routing']:

                    self.actual_trip.append(self.trip[to_leg])
                    x, y = self.trip[to_leg]
                    #print('%s just finished %s->%s' % (self.id, x, y))

                    self.__report(x, y, leg_duration)
                    leg_duration = 0

                    if 'decision_node' in self.sim.graph.node[y] and decision_count % 5 == 0:

                        decision_count += 1

                        self.needs_reroute = True

                        route = self.__route(self.trip[to_leg][1], self.end_node)

                        new_trip = []
                        new_trip.extend(self.actual_trip)
                        new_trip.extend(route)

                        # print('New route: %s' % route)

                        if (new_trip != self.trip):
                            print('Rerouting %s' % self.id)
                            # print('Old trip: %s' % self.trip)
                            # print('So far: %s' % self.actual_trip)
                            # print('Route: %s' % route)
                        self.trip = new_trip

                # pick the next leg, and start over
                to_leg += 1
                to_cell = 0

                continue

            # calculate the desired headway
            target_headway = int(self.current_speed / 5)
            # print(target_headway)

            # look ahead to determine the actual headway
            headway = self.__look(to_leg, to_cell, target_headway + 1)

            # print('Current speed: %s' % self.current_speed)
            # print('Needed Headway: %s' % target_headway)
            # print('Headway: %s' % (headway))

            # if there's more headway than needed
            if headway > target_headway:

                # calcuate the driver's desired speed
                ffs = from_arc['ffs']
                target_speed = ffs + self.target_speed_adjustment

                # random variations in ability to maintain speed
                # 50% chance of slowing down 1m/s
                if target_speed >=1 and random.randint(0, 1) == 0:
                    target_speed -= 1

                # print('Target speed %s' % (target_speed))

                # if self.id == 0:
                #     target_speed = target_speed / 10

                # vf = sqrt(vi^2 + 2ax)
                final_speed = np.sqrt((self.current_speed ** 2) + (2 * acceleration * distance))
                # print('Final speed would be %s if accelerating' % final_speed)

                # if car reaches target speed this segment
                if final_speed >= target_speed:

                    # print('Already Reached Target Speed')

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
                leg_duration += t
                self.total_driving_time += t
                yield self.sim.env.timeout(t)

            elif headway == 0:

                # if there's no headway, re-evaluate in a bit
                # print('no headway')
                if headway == 0:
                    t = self.sim._config['driver_reaction_time_s']
                    leg_duration += t
                    yield self.sim.env.timeout(t)
                    self.total_driving_time += t
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
                leg_duration += t
                self.total_driving_time += t
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
                leg_duration += t
                self.total_driving_time += t
                yield self.sim.env.timeout(t)

