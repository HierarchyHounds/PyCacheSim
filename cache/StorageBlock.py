class StorageBlock(object):
	def __init__(self, debugger):
		self.address = None
		self.index = None
		self.tag = 0
		self.dirty = False
		self.valid = False
		self.debugger = debugger
		self.metadata = {}

	def set_dirty(self):
		self.dirty = True
		self.debugger.log("set dirty")
		return self

	def invalidate(self, writeDirectlyToMemory=False):
		self.valid = False
		self.debugger.invalidated(self, writeDirectlyToMemory)
		return self

	def store(self, address, index, tag, block_address):
		self.address = address
		self.index = index
		self.tag = tag
		self.dirty = False
		self.valid = True
		self.block_address = block_address
		return self
