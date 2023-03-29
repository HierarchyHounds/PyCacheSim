from collections import deque
from .Policy import Policy

class FIFO(Policy):
    def __init__(self, num_sets, associativity):
        super().__init__(num_sets, associativity)
        self.cache_sets = [deque() for _ in range(num_sets)]

    def evict(self, index):
        evicted_block = self.cache_sets[index].popleft()
        return evicted_block

    def insert(self, block):
        index = block.index
        self.cache_sets[index].append(block)

    def update(self, block):
        pass  # No action is needed for FIFO on access
