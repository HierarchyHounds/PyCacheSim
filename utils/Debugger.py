def getOperationName(operation):
	if operation == "r":
		return "read"
	if operation == "w":
		return "write"
	raise ValueError(f"Invalid operation: {operation}")

class Debugger:
	debug = False

	def __init__(self, counter=None, prefix=""):
		self.counter = counter
		self.prefix = prefix

	def log(self, *args):
		if not Debugger.debug: return
		print(self.prefix, *args)

	def operationStart(self, operation, address):
		if not Debugger.debug: return
		if not self.counter: return
		program_counter = self.counter.get()
		print("----------------------------------------")
		print(f"# {program_counter} : {getOperationName(operation)} {address}")

	def operation(self, operation, block_address, tag, index):
		if not Debugger.debug: return
		print(self.prefix, getOperationName(operation), f": {block_address:x} (tag {tag:x}, index {index})")

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

		print(self.prefix, f"victim: {block.block_address:x} (tag {block.tag:x}, index {block.index}, {status})")

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
