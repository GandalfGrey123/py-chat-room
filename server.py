# Author - Marcus Wong
# Date created - February 28, 2019 
# Python3 Version - 3.7.2

import socket
import select
import signal
import sys
import time
from subprocess import Popen

import random
import string

from resources.users.user import User
from resources.paths.path_master import *

HOST_IP = "localhost"
DEFAULT_PORT = 3000
SOCKET_BUFFER_SIZE = 1000

ports_in_use = []

#create single server listening socket to handle all client requests
server_sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )

#setup list of file descriptors to monitor
reader_fds = []
reader_fds.append(sys.stdout)
reader_fds.append(sys.stdin)
reader_fds.append(server_sock)


#cache logged in user with hashmap
#key <file descriptor> : value User obj
current_users = {}



###########################
# Fake Database Functions #
###########################


#unique key builder for each user inbox
def id_generator(size=4, chars=string.ascii_uppercase + string.digits):
    id = ''.join(random.choice(chars) for _ in range(size))
    return "#"+id



#get list of all usernames from database
def user_list():
	db = open(USER_DB_PATH,"r")
	all_users = list()
	for user_data in db.readlines():
		all_users.append( user_data.partition(' ')[0].rstrip() )
	db.close()
	return all_users



#search and check for username in the database
def user_search(username):
	if username in user_list():
		return True
	else:
		return False

#return user's inbox key
def user_inbox_key(username):
	db = open(USER_DB_PATH,"r")

	for next_row in db.readlines():
		user_info = next_row.split()
		if user_info[0] == username:
			return user_info[2]

def login_verify(username,password):
	db = open(USER_DB_PATH,"r")

	for next_row in db.readlines():
		user_data = next_row.split()
		if user_data[0] == username and user_data[1] == password:
			return True
	db.close()
	return False




###########################
# SERVER SYSTEM FUNCTIONS #
###########################


#handles regular shutdown and exception shutdown
def server_shutdown():
	print("Shuting down server ... ")
	#close all file descriptors, skip stdout and stdin
	for fds in reader_fds[2:]:
		fds.close()
	exit()


#returns a User object from list of currently logged in users
def get_user(fd):
	return current_users[fd]	









##########################
# CLIENT REQUEST HELPERS #
##########################

#create a new file to store user inbox messages using key as filename
def create_new_inbox():
	
	#keep creating random keys if key name already exists
	not_succ = True
	max_tries = 0 #infinite loop control
	
	while not_succ and max_tries < 10:
		key = id_generator()

		try:			
			file = open(USER_INBOX_PATH+key, 'w')
			not_succ = False
			file.close()

		except IOError:				
			if max_tries == 9:
				return False		 
			max_tries+=1
			pass

	return key


#takes string in format, "username password" and add to user-db
def add_new_user(user_info):
	user_info = user_info.split()

	#check if user exists
	if user_search(user_info[0]) == True:
		print("did not add the new user to database")
		return False

	#create new inbox and get the reference filename
	inbox_key = create_new_inbox() 
	if inbox_key != False:

		print("adding the new user to database")
		#save the user data in the database
		db = open(USER_DB_PATH,"a")
		db.write(user_info[0]+" "+ user_info[1]+" "+inbox_key+"\n")
		db.close()
		return True

	else:
		return False


#return a string of all users
def show_user_list():
	user_set = user_list()
	l = ""
	for user in user_set:
		l += user + " "
	return l

#return a string of all user's messages
def get_inbox(inbox_key):
	inbox = open(USER_INBOX_PATH+inbox_key,"r")
	messages=""
	for data in inbox.readlines():
		messages += data + "\n"
	return messages


#sending messages between users
def direct_message_to(to,message,from_user):
	key = user_inbox_key(to)
	to_inbox = open(USER_INBOX_PATH+key,"a")
	to_inbox.write("\nFrom: " + from_user + "\n" + message +"\n end \n")
	to_inbox.close()


# SERVE REQUEST TYPE COMING FROM CLIENT SOCKET
def handle_user_request(client_sock,request):
	print("Handling a request .. ")

	#user requet to login
	if request == "lo":
		client_sock.send("Logging in user..".encode('utf8'))
		user_info = client_sock.recv(SOCKET_BUFFER_SIZE).decode('utf8')
		user_info = user_info.split()
		
		#if valid login, cache User info and send success
		if login_verify(user_info[0],user_info[1]) == True:
			client_sock.send("1".encode('utf8'))
			current_users[client_sock]= User(client_sock, user_info[0],user_inbox_key(user_info[0]))
			print("A user has logged in")
		else:
			client_sock.send("Login unsuccessful!".encode('utf8'))
			print("A user login attempt has failed")



		

	#request for new user account
	elif request == "cu":
		client_sock.send("Creating your user account..".encode('utf8'))
		
		#recieve client login info in format "username password"
		user_info = client_sock.recv(SOCKET_BUFFER_SIZE).decode('utf8')
		
		#if username does not exist , send success to client
		if add_new_user(user_info) == True:
			client_sock.send("1".encode('utf8'))

		#else username does exist , send failure to client
		else:			
			client_sock.send("\n!! ERROR !! \n User already exists!".encode('utf8'))



	#user is requesting username list
	elif request == "gu":
		print("sending client list")
		users = show_user_list()
		client_sock.send(users.encode('utf8'))




	#user is requesting inbox messages
	elif request == "inb":
		 print("sending client inbox")
		 messages = get_inbox(current_users[client_sock].inbox_key)
		 if messages == "":
		 	messages = "inbox is empty! "
		 client_sock.send(messages.encode('utf8'))		




	#user is trying to send email
	elif request == "msg":
		client_sock.send("sending an email .. ".encode('utf8'))
		username = client_sock.recv(SOCKET_BUFFER_SIZE).decode('utf8')
		
		if user_search(username) == True:
			client_sock.send("1".encode('utf8'))
			message = client_sock.recv(SOCKET_BUFFER_SIZE).decode('utf8')
			print("message: " + message)

			from_user = get_user(client_sock).username

			#send from username, to username and message
			direct_message_to(username,message,from_user)
			client_sock.send("\nmessage succesfully sent! \n".encode('utf8'))

		else:
			client_sock.send("\nthis username does not exist..\n".encode('utf8'))




	#client requesting new chat room
	elif request == "nc":
		client_sock.send("creating a new chat room .. ".encode('utf8'))
		
		port = client_sock.recv(SOCKET_BUFFER_SIZE).decode('utf8')
		if port not in ports_in_use:
			
						
			ports_in_use.append(int(port))
			p = Popen(["python3","chatroom.py",str(port)], shell=False,stdin=None, stdout=None, stderr=None, close_fds=True)
			time.sleep(2)

			#notify client that chat room is running
			client_sock.send("1".encode('utf8'))
			
			#disconnect client after they connect to chat
			client_sock.close()
			reader_fds.remove(client_sock)

		else:
			client_sock.send("port already in use".encode('utf8'))
	
	
	#disconnect a user 
	elif request == "di":
		print("Client disconnecting .. ")					
		client_sock.close()

		#remove select list and logged in users cache
		reader_fds.remove(client_sock)
		if len(current_users) !=0:
			del current_users[client_sock]




def run_server(port):

	server_sock.bind(( HOST_IP,port ))
	server_sock.listen()
	ports_in_use.append(port)

	while True:
		readers, _, _ = select.select(reader_fds,[],[])

		for sock in readers:
			
			#New connection
			if sock is server_sock:				
				print("Recieving new connection .. ")			
				conn, addr = server_sock.accept()
				reader_fds.append(conn)

				conn.send("\n\n Welcome to the server!".encode('utf8'))				 
				break
			
			#Serve a connected client
			else:
				for fds in reader_fds[3:]:
					if sock.fileno() == fds.fileno():
						next_msg = fds.recv(SOCKET_BUFFER_SIZE).decode('utf8')
						handle_user_request(fds,next_msg)					



# - Main Code - #					

def main():
	try:
		port = int(sys.argv[1])
		run_server(port)
	 
	except KeyboardInterrupt:
		server_shutdown()

main()



