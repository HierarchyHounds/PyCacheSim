class StorageBlock(object):
	def __init__(self, debugger):
		self.address = None
		self.index = None
		self.tag = None
		self.dirty = False
		self.valid = False
		self.debugger = debugger

	def set_dirty(self):
		self.dirty = True
		self.debugger.log("set dirty")
		return self

	def invalidate(self):
		self.valid = False
		return self

	def store(self, address, index, tag):
		self.address = address
		self.index = index
		self.tag = tag
		self.dirty = False
		self.valid = True
		return self
