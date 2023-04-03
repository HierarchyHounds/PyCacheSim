import math
from collections import defaultdict
from policies.Policy import Policy

class Optimal(Policy):
	def __init__(self, counter, trace_file, block_size, debugger=None):
		super().__init__(counter)
		self.debugger = debugger
		offset_bits = int(math.log2(block_size))
		self.future = self.read_trace_file(trace_file, offset_bits)

	def read_trace_file(self, trace_file, offset_bits):
		future = defaultdict(list)

		with open(trace_file, "r") as file:
			for line_number, line in enumerate(file):
				if len(line.strip()) == 0:
					continue
				operation, address = line.strip().split(" ")
				address = int(address, 16) >> offset_bits << offset_bits
				future[address].append(line_number)

		return future

	def insert(self, block):
		pass

	def update(self, block):
		current_counter = self.counter.get()
		future = self.future[block.block_address]
		while future and future[0] < current_counter:
			future.pop(0)

	def remove(self, block):
		pass

	def evict(self, cache_set):
		max_distance = -1
		evicted_block = None
		current_counter = self.counter.get()

		for block in cache_set:
			self.update(block)
			future = self.future[block.block_address]

			# # print the first 10 elements of future # TODO: remove
			# if len(future) > 10:
			# 	self.log(
			# 		f"Address: {block.block_address:x}, Future: {future[:10]}")
			# else:
			# 	self.log(f"Address: {block.block_address:x}, Future: {future}")

			# if a block is never needed again, evict it
			if not future:
				return block

			# find the farthest future access
			distance = future[0] - current_counter
			if distance > max_distance:
				max_distance = distance
				evicted_block = block

		return evicted_block

	def log(self, *args):
		if not self.debugger:
			return
		self.debugger.log(*args)
