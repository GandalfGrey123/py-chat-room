from abc import ABC, abstractmethod 

class AbstractAction(ABC):
	@abstractmethod
	def execute(self):
		pass

class ExitAction(AbstractAction):
	def __init__(self):
		self.type = 'text'

	def execute(self):
		print('executing')