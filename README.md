# py-chat-room

***

## Brief summary

This is a simple chat program written in python

Demo --> *Scroll to the bottom for a video link demo of this program*

###  Features & Implementation , brief

py-chat-room implements asynchronous IO to handle chat messaging and multiple user connections

py-chat-room uses sub processing to create multiple chat rooms 

py-chat-room has a simple username login / creation which also includes user inbox emailing system 







### Server Code Snippet - TCP connection handling

> The main approach / barebones used by the server and chat room programs , they use the `select` function from the python `select` module to handle incomming TCP conenctions and messages 

```python
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
```						







***

## Installation / Execution

#### Required install
	must install python3

#### How to run Client:
	run command => "python3 client.py"


#### How to run Server:
	run command => "python3 server.py <portno>"


***

## Recommended:
	
	
	Use long height for the Client terminal screen (output and menu can be large)

	
	you can create your own account or use test accounts ... 

	test user accounts
	1 username: test_user 
	  password: 123 

	2 username: foo_user 
	  password: 123  

	user account info can be viewed in plain text file /resources/users/user-db 
	
# Demo

A quick demonstration of multiple user login and chatrooms being handled simultaneously 

[![IMAGE ALT TEXT HERE](http://img.youtube.com/vi/sMmpfk4xrHU/0.jpg)](https://www.youtube.com/watch?v=sMmpfk4xrHU)


