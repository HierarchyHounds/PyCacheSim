from collections import deque

class Policy:
    def __init__(self, num_sets, associativity):
        pass

    def insert(self, block):
        raise NotImplementedError("Not implemented!")

    def update(self, block):
        raise NotImplementedError("Not implemented!")

    def evict(self, index):
        raise NotImplementedError("Not implemented!")
