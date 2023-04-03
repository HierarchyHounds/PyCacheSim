def getOperationName(operation):
	if operation == "r":
		return "read"
	if operation == "w":
		return "write"
	raise ValueError(f"Invalid operation: {operation}")

class Debugger:
	debug = False

	def __init__(self, prefix=""):
		self.prefix = prefix
		self.actionCounter = 0
		self.offset_bits = 0

	def log(self, *args):
		if not Debugger.debug: return
		print(self.prefix, *args)

	def operationStart(self, operation, address):
		if not Debugger.debug: return
		self.actionCounter += 1
		print("----------------------------------------")
		print(f"# {self.actionCounter} : {getOperationName(operation)} {address}")

	def operation(self, operation, address, tag, index):
		if not Debugger.debug: return

		# Remove offset bits
		if self.offset_bits:
			address = address >> self.offset_bits
			address = address << self.offset_bits

		print(self.prefix, getOperationName(operation), f": {address:x} (tag {tag:x}, index {index})")

	def policyUpdate(self):
		if not Debugger.debug: return
		print(self.prefix, "update", Debugger.policyClassName)

	def victim(self, block):
		if not Debugger.debug: return
		if block == None:
			print(self.prefix, "victim: none")
			return
		if block.dirty:
			status = "dirty"
		else:
			status = "clean"

				# Remove offset bits
		if self.offset_bits:
			address = block.address >> self.offset_bits << self.offset_bits

		print(self.prefix, f"victim: {address:x} (tag {block.tag:x}, index {block.index}, {status})")

	def invalidated(self, block, writeDirectlyToMemory=False):
		if not Debugger.debug: return
		if block == None:
			print(self.prefix, "invalidated: none")
			return
		if block.dirty:
			status = "dirty"
		else:
			status = "clean"

		# Remove offset bits
		if self.offset_bits:
			address = block.address >> self.offset_bits << self.offset_bits

		print(self.prefix, f"invalidated: {address:x} (tag {block.tag:x}, index {block.index}, {status})")

		if block.dirty and writeDirectlyToMemory:
			print(self.prefix, "writeback to main memory directly")

	def print_cache_set(self, cache, index):
		if not Debugger.debug: return
		print(self.prefix, "cache dump:", f"Set {index}:", end=" ")
		memory_set = cache.memory[index]
		for block in memory_set:
			dirty_flag = "D" if block.dirty else " "
			print(f"{block.tag:6x} {dirty_flag}  ", end="")
		print()
