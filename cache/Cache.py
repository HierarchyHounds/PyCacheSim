import math

class StorageBlock(object):
	def __init__(self, address, index, tag):
		self.address = address
		self.index = index
		self.tag = tag
		self.dirty = False
		self.valid = True

	def set_dirty(self):
		self.dirty = True

	def is_dirty(self):
		return self.dirty

class Cache:
	def __init__(self, size, associativity, block_size, PolicyClass, inclusion_property, lower_cache=None, debugger=None):
		self.num_sets = size // (associativity * block_size)
		self.memory = [[] for _ in range(self.num_sets)]
		self.index_bits = int(math.log2(self.num_sets))
		self.offset_bits = int(math.log2(block_size))

		self.size = size
		self.associativity = associativity
		self.block_size = block_size
		self.policy = PolicyClass(self.num_sets, associativity)
		self.inclusion_property = inclusion_property
		self.debugger = debugger
		self.lower_cache = lower_cache

		self.reads = 0
		self.read_misses = 0
		self.writes = 0
		self.write_misses = 0
		self.writebacks = 0
		self.memory_accesses = 0

	def calculate_index_tag(self, address):
		# Remove offset bits
		address = address >> self.offset_bits
		# Extract index bits
		index = address & ((1 << self.index_bits) - 1)
		# Remaining bits are tag bits
		tag = address >> self.index_bits
		return index, tag

	def find_block(self, index, tag):
		for block in self.memory[index]:
			if block.tag == tag:
				return block
		return None

	def create_and_insert_block(self, address):
		index, tag = self.calculate_index_tag(address)
		block = StorageBlock(address, index, tag)
		index = block.index
		self.memory[index].append(block)
		return block

	def remove_block(self, block):
		index = block.index
		self.memory[index].remove(block)

	def is_set_full(self, index):
		return len(self.memory[index]) >= self.associativity

	def print_contents(self):
		for i, memory_set in enumerate(self.memory):
			print(f"Set\t{i}:", end="\t")
			for block in memory_set:
				dirty_flag = "D" if block.dirty else " "
				print(f"{block.tag:6x} {dirty_flag}", end="  ")
			print()

	def get_miss_rate(self):
		if self.reads + self.writes == 0:
			return 0
		miss_rate = (self.read_misses + self.write_misses) / (self.reads + self.writes)
		return round(miss_rate, 6)

	def access(self, operation, address):
		index, tag = self.calculate_index_tag(address)
		self.debugger.operation(operation, address, tag, index)

		block = self.find_block(index, tag)

		if block:
			return self.handle_cache_hit(operation, block)
		else:
			return self.handle_cache_miss(operation, address, index)

	def handle_cache_hit(self, operation, block):
		if operation == 'r':
			self.reads += 1
			self.debugger.log(f"read : {block.address:x} (tag {block.tag:x}, index {block.index:x})")
		elif operation == 'w':
			self.writes += 1
			self.debugger.log(f"write : {block.address:x} (tag {block.tag:x}, index {block.index:x})")
			block.set_dirty()
			self.debugger.log("set dirty")
		self.policy.update(block)
		self.debugger.policyUpdate()
		return block

	def handle_cache_miss(self, operation, address, index):
		self.debugger.log("miss")
		if operation == 'r':
			self.reads += 1
			self.read_misses += 1
		elif operation == 'w':
			self.writes += 1
			self.write_misses += 1

		block = self.load_block_from_memory(operation, address, index)
		if operation == 'w':
			block.set_dirty()
			self.debugger.log("set dirty")
		return block

	def load_block_from_memory(self, operation, address, index):
		if self.lower_cache:
			block = self.lower_cache.access(operation, address)
			if not block:
				return None

			if self.is_set_full(index):
				evicted_block = self.policy.evict(index)
				self.debugger.victim(evicted_block)
				self.remove_block(evicted_block)
				if evicted_block.is_dirty():
					self.writebacks += 1

			if self.inclusion_property == 1:  # inclusive
				copied_block = self.create_and_insert_block(block.address)
				self.policy.insert(copied_block)
				self.debugger.policyUpdate()
				return copied_block
			elif self.inclusion_property == 0:  # non-inclusive
				new_block = self.create_and_insert_block(address)
				self.policy.insert(new_block)
				self.debugger.policyUpdate()
				return new_block
		else:
			if self.is_set_full(index):
				evicted_block = self.policy.evict(index)
				self.debugger.victim(evicted_block)
				self.remove_block(evicted_block)
				if evicted_block.is_dirty():
					self.writebacks += 1

			new_block = self.create_and_insert_block(address)
			self.policy.insert(new_block)
			self.debugger.policyUpdate()
			return new_block
