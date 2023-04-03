class Counter:
	def __init__(self):
		self.value = 0
		self.subscribers = []

	def subscribe(self, callback):
		self.subscribers.append(callback)

	def increment(self):
		self.value += 1
		for callback in self.subscribers:
			callback(self.value)
		return self.value

	def get(self):
		return self.value
