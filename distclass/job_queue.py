import time
import collections

class JobQueue(object):

    queue = None
    
    def __init__(self):
        self.queue = collections.deque()

    def append(self, element):
        self.queue.append(element)

    def popleft(self):
        while len(self.queue) == 0:
            time.sleep(0.001)

        element = self.queue.popleft()
        return element

    def copy(self):
        cpy = JobQueue()
        cpy.queue = self.queue.copy()

        return cpy

    def __iter__(self):
        return self.queue.__iter__()
