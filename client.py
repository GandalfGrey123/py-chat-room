# Author - Marcus Wong
# Date created - February 28, 2019 
# Python3 Version - 3.7.2

import socket
import select
import sys



CLIENT_USERNAME = ""
LOGGED_IN = False
CONNECTED = False
SOCKET_BUFFER_SIZE = 1000
IN_CHAT= False

#Global socket for client to communicate to server
client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
chat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

SERVER_IP = ""




main_menu = '''

      ----------Command Options--------------

		0. Connect to server
		1. Login
		2. Create user
		3. Get user list
		4. Display inbox messages
		5. Send email message
		6. Create chat room
		7. Connect to chat room

	type \'exit()\' to exit
      ---------------------------------------

			   '''

###########################
# CLIENT SYSTEM FUNCTIONS #
###########################


def server_disconnect():
	print("Disconnecting ...  ")
	client_sock.send("di".encode('utf8'))

def interface_shutdown():
	if CONNECTED == True:
		server_disconnect()

	if IN_CHAT == True:
		client_sock.close()

	print("shutting down")
	sys.exit(0)


def set_logged_in(flag):
	global LOGGED_IN
	LOGGED_IN = flag

def set_connected(flag):
	global CONNECTED
	CONNECTED = flag

def set_username(name):
	global CLIENT_USERNAME
	CLIENT_USERNAME = name		

def set_in_chat(flag):
	global IN_CHAT
	IN_CHAT = flag	




##########################
###   Menu Functions   ###
##########################

def connect_to_server():
	SERVER_IP = input("enter an ip address: ")	
	port = input("enter a port number: ")	
	client_sock.connect((SERVER_IP,int(port)))		
	
	global CONNECTED
	CONNECTED = True

	#recieve the welcome message
	print(client_sock.recv(SOCKET_BUFFER_SIZE).decode('utf8'))


def login():
	if not CONNECTED:
		print("you must connect first!")
	else:
		if send_credentials("lo") == True:
			print("Hello, " + CLIENT_USERNAME + ".")
			print("You are now logged in! ")

def create_user():
	if send_credentials("cu") == True:
		print("account created!")
		print("you must log in to your account")

def send_credentials(type):
	username = input("enter a username: ")	
	password = input("enter a password: ")

	#MUST NOT CONTAIN SPACES
	#local validation username and password ...

	print("\n\n")
	client_sock.send(type.encode('utf8'))
	print(client_sock.recv(SOCKET_BUFFER_SIZE).decode('utf8'))
	
	client_sock.send((username+" "+password).encode('utf8'))
	resp = client_sock.recv(SOCKET_BUFFER_SIZE).decode('utf8')

	if resp == "1":

		set_logged_in(True)
		set_connected(True)
		set_username(username)
		return True
		 
	else:
		print(resp)
	


def get_user_list():
	client_sock.send("gu".encode('utf8'))
	resp = client_sock.recv(SOCKET_BUFFER_SIZE).decode('utf8')
	print("CLIENT USERNAME LIST")
	print("------------")
	
	for user in resp.split():
		print(user)

	print("\n")




def view_inbox():
	if not LOGGED_IN:
		print("you must log in first")
		return

	print("Showing your inbox")
	client_sock.send("inb".encode('utf8'))
	resp = client_sock.recv(SOCKET_BUFFER_SIZE).decode('utf8')
	print("All Messages: ")
	print("------------")
	print(resp)




def send_email():
	if not LOGGED_IN:
		print("you must log in first")
		return

	client_sock.send("msg".encode('utf8'))
	print(client_sock.recv(SOCKET_BUFFER_SIZE).decode('utf8'))
	
	username = input("enter username to send message to: ")	
	client_sock.send(username.encode('utf8'))
	resp = client_sock.recv(SOCKET_BUFFER_SIZE).decode('utf8')
	
	#if valid username
	if resp == "1":
		message = input("enter your message: ")
		client_sock.send(message.encode('utf8'))
		print(client_sock.recv(SOCKET_BUFFER_SIZE).decode('utf8'))

	#else not , abort
	else:
		print(client_sock.recv(SOCKET_BUFFER_SIZE).decode('utf8'))





def run_chat(chat_socket):

	while True:	

		readers, _, _ = select.select([sys.stdin,chat_socket],[],[])		
	
		for reader in readers:

			if reader is chat_socket:				
				print(chr(27)+'[2A\n')
				resp = chat_socket.recv(SOCKET_BUFFER_SIZE).decode('utf8')
				
				if resp == "di":
					chat_socket.close()
					print("sorry server is down")
					return
				else:
					print(resp)			
					print(CLIENT_USERNAME + ': ', end='', flush=True)

			else: #reader is sys.stdin:
				
				next_msg = input(CLIENT_USERNAME + ': ')
				
				if next_msg == "disconnect()":
					chat_socket.send("di".encode('utf8'))
					chat_socket.close()
					return
				
				chat_socket.send((CLIENT_USERNAME+": "+next_msg) .encode('utf8'))
				
		
			


def new_chat_room():
	if not LOGGED_IN:
		print("you must log in first")
		return	

	#send a request to server to open port
	client_sock.send("nc".encode('utf8'))
	print(client_sock.recv(SOCKET_BUFFER_SIZE).decode('utf8'))
	
	port = input("enter a chat port number: ")
	client_sock.send(port.encode('utf8'))
	resp = client_sock.recv(SOCKET_BUFFER_SIZE).decode('utf8')
	if resp == "1":
		chat_socket.connect((SERVER_IP,int(port)))
		set_in_chat(True)
		run_chat(chat_socket)
		set_in_chat(False)
	else:
		print(resp)
	#need to close client and server side socket

	
def connect_to_room():
	port = input("enter a chat port number: ")
	chat_socket.connect((SERVER_IP,int(port)))
	run_chat(chat_socket)
	


menu_dispatch = {
	'0':connect_to_server,
	'1':login,
  	'2':create_user,
  	'3':get_user_list,
  	'4':view_inbox,
  	'5':send_email,
	'6':new_chat_room,
	'7':connect_to_room, 
	'exit()':interface_shutdown
}




def run():
	 
	#must be connected to server, loop till connected
	while True:

		print(main_menu)
		menu_choice = input('> ')
		print('\n\n')

		if menu_choice in menu_dispatch.keys():			
			menu_dispatch[menu_choice]()			
		else:
			print("\n Invalid option! \n")



# - Main Code - #					

try:
    run()

except KeyboardInterrupt:
	interface_shutdown()

	if IN_CHAT == True:
		chat_socket.close()
    
   


