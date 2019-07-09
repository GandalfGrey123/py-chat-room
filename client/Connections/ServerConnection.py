import socket

class ServerConnection:
	def __init__(self, port, host_name_ip):
		self.port = port
		self.host_name_ip = host_name_ip
		self.main_sock = None
   
    #test timeout tolerance is 10 seconds
	def test_connection(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.settimeout(10)
		try:
			sock.connect((self.host_name_ip,int(self.port)))
			return True
		except:
			return False
		finally:
			sock.close()

	def is_connected(self):
		return self.main_sock != None

	#main handshake timeout tolerance is 3 seconds
	def connect_to_server_successfully(self):
		self.main_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.main_sock.settimeout(10)
		try:
			self.main_sock.connect((self.host_name_ip,int(self.port)))
		except:	
			self.main_sock = None						
			return False		
		return True

	def close_connection_successful(self):
		if self.is_connected(): 
			self.main_sock.close()
			self.main_sock = None
			return True
		else:
			return False
