import math

from policies.Policy import Policy

class FIFO(Policy):
	def __init__(self, counter):
		super().__init__(counter)

	# track insertion time
	def insert(self, block):
		block.metadata['inserted'] = self.counter.get()

	# in case of FIFO, do nothing
	def update(self, block):
		pass

	def remove(self, block):
		pass

	# evict the block with the lowest insertion time
	def evict(self, cache_set):
		min_inserted = math.inf
		evicted_block = None
		for block in cache_set:
			inserted = block.metadata['inserted']
			if inserted < min_inserted:
				min_inserted = inserted
				evicted_block = block
		return evicted_block
