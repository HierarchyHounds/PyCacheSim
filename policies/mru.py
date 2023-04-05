import math
import time

from policies.Policy import Policy

class MRU(Policy):
	def __init__(self, counter):
		super().__init__(counter)

	# add required metadata to the block
	def insert(self, block):
		block.metadata['last_access'] = time.time()

	# update last_access
	def update(self, block):
		block.metadata['last_access'] = time.time()

	def remove(self, block):
		pass

	# evict the block with the highest last_access
	def evict(self, cache_set):
		max_last_access = -math.inf
		evicted_block = None
		for block in cache_set:
			last_access = block.metadata['last_access']
			if last_access > max_last_access:
				max_last_access = last_access
				evicted_block = block
		return evicted_block
