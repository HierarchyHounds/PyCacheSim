import math


class StorageBlock(object):
	def __init__(self, address, index, tag):
		self.address = address
		self.index = index
		self.tag = tag
		self.dirty = False
		# self.valid = True

	def set_dirty(self):
		self.dirty = True

	def is_dirty(self):
		return self.dirty

class Cache:
	def __init__(self, size, associativity, block_size, PolicyClass, inclusion_property):
		self.num_sets = size // (associativity * block_size)
		self.memory = [[] for _ in range(self.num_sets)]
		self.index_bits = int(math.log2(self.num_sets))
		self.offset_bits = int(math.log2(block_size))

		self.size = size
		self.associativity = associativity
		self.block_size = block_size
		self.policy = PolicyClass(self.num_sets, associativity)
		self.inclusion_property = inclusion_property

		self.reads = 0
		self.read_misses = 0
		self.writes = 0
		self.write_misses = 0
		self.writebacks = 0
		self.memory_accesses = 0

	def calculate_index_tag(self, address):
		address = address >> self.offset_bits  # Remove offset bits
		index = address & ((1 << self.index_bits) - 1)  # Extract index bits
		tag = address >> self.index_bits  # Remaining bits are tag bits
		return index, tag

	def get_block(self, address):
		"""
		Retrieves a block from the cache based on the address.
		Returns the block if it exists, otherwise returns None.
		"""
		index, tag = self.calculate_index_tag(address)

		for block in self.memory[index]:
			if block.tag == tag:
				return block

		# for line_id, block in enumerate(self.memory[index]):
		# 	print(block.data)
		# 	if block.tag == tag:
		# 		return True ,line_id

		return None
		# raise NotImplementedError("get_block function must be implemented in the Cache class")

	def create_block(self, address):
		index, tag = self.calculate_index_tag(address)
		new_block = StorageBlock(address, index, tag)
		index = new_block.index
		self.memory[index].append(new_block)
		return new_block

	def remove_block(self, block):
		index = block.index
		self.memory[index].remove(block)

	# def is_full(self):
	# 	for memory_set in self.memory:
	# 		if len(memory_set) < self.associativity:
	# 			return False
	# 	return True

	def is_set_full(self, index):
		return len(self.memory[index]) >= self.associativity

	def print_contents(self):
		for i, memory_set in enumerate(self.memory):
			print(f"Set\t{i}:", end="\t")
			for block in memory_set:
				dirty_flag = "D" if block.is_dirty() else " "
				print(f"{block.tag:6x} {dirty_flag}", end="  ")
			print()

	def get_miss_rate(self):
		if self.reads + self.writes == 0:
			return 0
		return (self.read_misses + self.write_misses) / (self.reads + self.writes)

	def access(self, operation, address, lower_cache=None):
		block = self.get_block(address)

		if block is not None:
			# Cache hit
			self.policy.update(block)
			if operation == 'w':
				block.set_dirty()
				self.writes += 1
			else:
				self.reads += 1
		else:
			# Cache miss
			if operation == 'w':
				self.write_misses += 1
				self.writes += 1
			else:
				self.read_misses += 1
				self.reads += 1

			if lower_cache:
				# Access the lower level cache
				lower_block = lower_cache.access(operation, address)

				if lower_block:
					# Evict a block from the current set if it's full
					if self.is_set_full(lower_block.index):
						evicted_block = self.policy.evict(lower_block.index)
						self.remove_block(evicted_block)
						if evicted_block.is_dirty():
							self.writebacks += 1

					# Handle inclusion_property properties and L1-L2 interaction
					if self.inclusion_property == 1:  # inclusive
						# Copy the block from L2 into L1
						copied_block = self.create_block(lower_block.address)
						self.policy.insert(copied_block)
						if operation == 'w':
							copied_block.set_dirty()
					elif self.inclusion_property == 0:  # non-inclusive
						# Load the block from L2 into L1
						new_block = self.create_block(address)
						self.policy.insert(new_block)
						if operation == 'w':
							new_block.set_dirty()
				else:
					# Load the block from memory if there is a miss in L2
					self.memory_accesses += 1
					new_block = self.create_block(address)
					index, _ = self.calculate_index_tag(address)
					self.policy.insert(new_block)
					if operation == 'w':
						new_block.set_dirty()

			else:
				# Load the block from memory and insert it into the cache
				self.memory_accesses += 1

				# Evict a block from the current set if it's full
				index, _ = self.calculate_index_tag(address)
				if self.is_set_full(index):
					evicted_block = self.policy.evict(index)
					self.remove_block(evicted_block)
					if evicted_block.is_dirty():
						self.writebacks += 1
						self.memory_accesses += 1

				new_block = self.create_block(address)
				self.policy.insert(new_block)
				if operation == 'w':
					new_block.set_dirty()

		return block
