class Policy:
	def __init__(self, counter):
		self.counter = counter

	# add necessary metadata to the block
	def insert(self, block):
		raise NotImplementedError("Not implemented!")

	# update metadata on access
	def update(self, block):
		raise NotImplementedError("Not implemented!")

	# remove block metadata as needed
	def remove(self, block):
		raise NotImplementedError("Not implemented!")

	# use metadata to select a block for eviction
	# this should only be called if all blocks in the set are valid
	def evict(self, cache_set):
		raise NotImplementedError("Not implemented!")
