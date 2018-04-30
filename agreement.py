class Agreement:
	def __init__(self, callback):
		self.local = None
		self.remote = None
		self.callback = callback

	def local_answer(self, answer):
		self.local = answer
		self.agree()

	def remote_answer(self, answer):
		self.remote = answer
		self.agree()

	def agree(self):
		if self.local == False:
			self.callback(False)
		elif self.local == True and self.remote is not None:
			self.callback(self.remote)