from Actions import ExitAction

class ActionBuilder:
	def build_action(self, action_class_name):
		return globals()[action_class_name]()
