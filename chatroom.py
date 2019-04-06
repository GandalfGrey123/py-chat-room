# Author - Marcus Wong
# Date created - February 28, 2019 
# Python3 Version - 3.7.2

import socket
import select
import signal
import sys
import time


HOST_IP = "localhost"
SOCKET_BUFFER_SIZE = 1000

room_sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )

#setup list of file descriptors to monitor
reader_fds = []
reader_fds.append(sys.stdout)
reader_fds.append(sys.stdin)
reader_fds.append(room_sock)


#must close all the sockets before exit()
def chat_shutdown():
	reader_fds.remove(room_sock)
	room_sock.close()

	for fds in reader_fds[2:]:
		print("closing socket: "+fds.fileno())

		#send shut down signal if chatroom exception occurs
		fds.send("di".encode('utf8'))
		fds.close()		
	exit()

def disconnect_client(from_client):
	from_client.close()

	#remove select list and logged in users cache
	reader_fds.remove(from_client)

	if len(reader_fds) == 3:
		print("Chat room has shutdown")
		chat_shutdown()


def send_message(message,from_client):

	if message == "di":
		disconnect_client(from_client)

	else:
		for fds in reader_fds[3:]:
			print(message)
			
			#skip the sending client's fd
			if from_client.fileno() != fds.fileno():
				fds.send(message.encode('utf8'))


def run_chat_room(port):

	room_sock.bind(( HOST_IP,port ))
	room_sock.listen()

	while True:
		readers, _, _ = select.select(reader_fds,[],[])

		for incomming_sock in readers:

			#Serve new connection
			if incomming_sock is room_sock:
				conn, addr = room_sock.accept()
				reader_fds.append(conn)
				conn.send("\nWelcome to the chat room!\n\n you MUST type disconnect() to disconnect..\n".encode('utf8'))
				break

			#Distribute message from client FD
			else:
				for client_fds in reader_fds[3:]:
					if incomming_sock.fileno() == client_fds.fileno():
						next_msg = client_fds.recv(SOCKET_BUFFER_SIZE).decode('utf8')
						send_message(next_msg,client_fds)	


def main():
	try:
		
		port = int(sys.argv[1])
		run_chat_room(port)
	 
	except KeyboardInterrupt:
		pass
	finally:
		chat_shutdown()
	    
main()	
