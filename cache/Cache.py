import math
from cache.StorageBlock import StorageBlock

class Cache:
	def __init__(self, size, associativity, block_size, PolicyClass, inclusion_property, lower_cache=None, upper_cache=None, debugger=None):
		self.num_sets = size // (associativity * block_size)
		# self.memory = [[] for _ in range(self.num_sets)]
		self.memory = [[StorageBlock(debugger) for _ in range(associativity)]
					   for _ in range(self.num_sets)]
		self.index_bits = int(math.log2(self.num_sets))
		self.offset_bits = int(math.log2(block_size))

		self.size = size
		self.associativity = associativity
		self.block_size = block_size
		self.policy = PolicyClass(self.num_sets, associativity)
		self.inclusion_property = inclusion_property
		self.debugger = debugger
		if debugger:
			debugger.offset_bits = self.offset_bits

		self.reads = 0
		self.read_misses = 0
		self.writes = 0
		self.write_misses = 0
		self.writebacks = 0
		self.memory_accesses = 0

		# establish cache hierarchy
		self.lower_cache = lower_cache
		self.upper_cache = upper_cache
		if self.lower_cache:
			self.lower_cache.upper_cache = self
		if self.upper_cache:
			self.upper_cache.lower_cache = self

	def calculate_index_tag(self, address):
		# Remove offset bits
		address = address >> self.offset_bits
		# Extract index bits
		index = address & ((1 << self.index_bits) - 1)
		# Remaining bits are tag bits
		tag = address >> self.index_bits
		return index, tag

	def increment_miss_counter(self, operation):
		if operation == 'r':
			self.read_misses += 1
		elif operation == 'w':
			self.write_misses += 1
		else:
			raise ValueError(f"Invalid operation: {operation}")

	def increment_counters(self, operation=None, memory_access=False, writeback=False):
		if memory_access:
			self.memory_accesses += 1
		if writeback:
			self.writebacks += 1
		if operation == 'r':
			self.reads += 1
		elif operation == 'w':
			self.writes += 1

	def is_set_full(self, index):
		return len(self.memory[index]) >= self.associativity

	# search for a given tag at a particular index
	# returns the block if found, None otherwise
	def search(self, index, tag):
		for block in self.memory[index]:
			if block.tag == tag and block.valid:
				return block
		return None

	# adds `address` to cache
	# evicts a block if necessary
	# returns the block that was updated
	def evict(self, index):
		# check all blocks in memory[index]
		# if any are invalid, replace
		for block in self.memory[index]:
			if not block.valid:
				self.debugger.victim(None)
				return block

		# no invalid blocks; evict
		block = self.policy.evict(index)
		self.debugger.victim(block)
		self.flush(block)
		block.valid = False

		# inclusive cache
		if self.inclusion_property == 1:
			# if upper cache exists, invalidate block there
			if self.upper_cache:
				self.upper_cache.invalidate(block.address)

		return block

	def invalidate(self, address):
		index, tag = self.calculate_index_tag(address)
		block = self.search(index, tag)
		if block is None: return

		writeDirectlyToMemory = block.dirty and self.inclusion_property == 1 and self.lower_cache is not None
		block.invalidate(writeDirectlyToMemory)
		self.policy.remove(block)
		self.flush(block, writeDirectlyToMemory)
		return block

	def flush(self, block, writeDirectlyToMemory=False):
		if not block.dirty: return block

		self.increment_counters(writeback=True)

		# if lower cache exists, write to it unless writeDirectlyToMemory flag is set
		if self.lower_cache and not writeDirectlyToMemory:
			self.lower_cache.access('w', block.address)
		else:
			self.increment_counters(memory_access=True)

		block.dirty = False
		return block

	def access(self, operation, address):
		index, tag = self.calculate_index_tag(address)
		self.debugger.operation(operation, address, tag, index)
		self.increment_counters(operation=operation)

		# block exists, cache hit
        # no eviction occurs here
		block = self.search(index, tag)
		if block:
			self.debugger.log("hit")
			self.policy.update(block)
			self.debugger.policyUpdate()

		else:
			# cache miss - block does not exist
			self.debugger.log("miss")
			self.increment_miss_counter(operation)

			# evict to make room for new block
			block = self.evict(index)

			# if lower cache exists, copy from it
			if self.lower_cache:
				self.lower_cache.access('r', address)
			# otherwise read the block from memory
			else:
				# block read from memory, so increment memory accesses
				self.increment_counters(memory_access=True)

			# block loaded; now add it to cache
			block.store(address, index, tag)
			self.policy.insert(block)
			self.debugger.policyUpdate()

		# for write operations, set dirty bit
		if operation == 'w':
			block.set_dirty()

		return block

	def get_contents(self):
		contents = ""
		for i, memory_set in enumerate(self.memory):
			contents += f"Set\t{i}:\t"
			for block in memory_set:
				dirty_flag = "D" if block.dirty else " "
				contents += f"{block.tag:6x} {dirty_flag}  "
			contents += "\n"
		return contents

	def get_miss_rate(self, read_operations_only=False):
		if read_operations_only:
			if self.reads == 0:
				return 0
			miss_rate = self.read_misses / self.reads
			return round(miss_rate, 6)

		if self.reads + self.writes == 0:
			return 0
		miss_rate = (self.read_misses + self.write_misses) / (self.reads + self.writes)
		return round(miss_rate, 6)
