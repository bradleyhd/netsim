from heapq import heappush, heappop, nsmallest
import itertools, sys

class PriorityQueue(object):

    def __init__(self):

        self.pq = []
        self.entry_finder = {}
        self.REMOVED = -1
        self.counter = itertools.count()

    def push(self, priority, node):

        if node in self.entry_finder:
            self._remove_node(node)

        n = next(self.counter)
        entry = [priority, n, node]
        self.entry_finder[node] = entry
        heappush(self.pq, entry)

    def _remove_node(self, node):
        entry = self.entry_finder.pop(node)
        entry[-1] = self.REMOVED

    def not_empty(self):

        while True:
            
            entries = nsmallest(1, self.pq)
            if not entries:
                return False

            if entries[0][2] == self.REMOVED:
                heappop(self.pq)
                continue

            return True

    def min_val(self):

        if self.not_empty():

            entries = nsmallest(1, self.pq)
            priority, count, node = entries[0]
            return priority

        else:

            return sys.maxsize

    def pop(self):
        while self.pq:
            priority, count, node = heappop(self.pq)
            if node is not self.REMOVED:
                del self.entry_finder[node]
                return [priority, node]
        raise KeyError('pop from an empty priority queue')