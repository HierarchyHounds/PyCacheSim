import math
import time

from policies.Policy import Policy

class LFU(Policy):
	def __init__(self, counter):
		super().__init__(counter)

	# add required metadata to the block
	def insert(self, block):
		block.metadata['accessed'] = 0

	# update last_access
	def update(self, block):
		block.metadata['accessed'] += 1

	def remove(self, block):
		pass

	# evict the block with the lowest accessed
	def evict(self, cache_set):
		min_accessed = math.inf
		evicted_block = None
		for block in cache_set:
			accessed = block.metadata['accessed']
			if accessed < min_accessed:
				min_accessed = accessed
				evicted_block = block
		return evicted_block

