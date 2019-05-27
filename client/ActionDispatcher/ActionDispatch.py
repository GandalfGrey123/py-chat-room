from ActionBuilder import ActionBuilder

class ActionDispatch:
	def __init__(self):
		self.actionBuilder = ActionBuilder()			

	def dispatch(self,command):
		if command in self.menu_options.keys():			
			self.menu_options[command]() 
		else:
			return None