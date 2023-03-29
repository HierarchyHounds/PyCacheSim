def getOperationName(operation):
	if operation == "r":
		return "read"
	if operation == "w":
		return "write"
	return "INVALID"


class Debugger:
	def __init__(self, prefix=""):
		self.prefix = prefix
		self.actionCounter = 0

	def log(self, *args):
		if Debugger.debug:
			print(self.prefix, *args)

	def operationStart(self, operation, address):
		if Debugger.debug:
			self.actionCounter += 1
			print("----------------------------------------")
			print(f"{self.actionCounter} : {getOperationName(operation)} {address}")

	def operation(self, operation, address, tag, index):
		if Debugger.debug:
			print(self.prefix, getOperationName(operation), f": {address:x} (tag {tag:x}, index {index})")

	def policyUpdate(self):
		if Debugger.debug:
			print(self.prefix, "update", Debugger.policyClassName)

	def victim(self, block):
		if Debugger.debug:
			if block == None:
				print(self.prefix, "victim: none")
				return
			if block.dirty:
				status = "dirty"
			else:
				status = "clean"
			print(self.prefix, f"victim: {block.address:x} (tag {block.tag:x}, index {block.index}, {status})")
