class User:

	client_sock = None
	username = None
	inbox_key = None

	def __init__(self,fd, name, key):
		self.client_sock = fd
		self.username = name
		self.inbox_key = key
