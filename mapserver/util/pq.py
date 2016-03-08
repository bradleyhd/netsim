from heapq import heappush, heappop
import itertools

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

    def pop(self):
        while self.pq:
            priority, count, node = heappop(self.pq)
            if node is not self.REMOVED:
                del self.entry_finder[node]
                return [priority, node]
        raise KeyError('pop from an empty priority queue')