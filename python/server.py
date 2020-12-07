# SE3313 Final Project Chat Server

from socket import *
from threading import Thread
import sys, select

# function to accept incoming connections
def accept_connection():
    
    while True:
        client, client_address = SERVER.accept() # get client and their address from incoming connection
        print("%s:%s has connected." % client_address)
        client.send(bytes("Type the name you wish to use.", "utf8"))
        adds[client] = client_address # store client address in list
        Thread(target=handle, args=(client,)).start()
        cons.append(client) # add client to list of sockets
       
        print("Type '{done}' to terminate")
        i, o, e = select.select([sys.stdin], [], [], 10)
        
        if (i):
            if (sys.stdin.readline().strip() == "{done}"):
                terminate()
        else:
            cmd = ""
            continue


# function to handle client actions by taking in a client
def handle(c): 

    name = c.recv(BUFFER).decode("utf8") # get client's name
    c.send(bytes("Type the name of the room you wish to join.", "utf8"))
    rooms[c] = c.recv(BUFFER).decode("utf8") # get room
    c.send(bytes("Welcome %s. Type '{help}' for more information." % name, "utf8")) # send welcome message
    broadcast(bytes("%s has joined the chat." % name, "utf8"), rooms[c]) # send global message
    clients[c] = name # add client to list of connected clients

    while True:
        cmsg = c.recv(BUFFER) # get client message
        
        if cmsg == bytes("{exit}", "utf8"): # cient is exiting
            c.close() # close client connection
            exit_room = rooms[c] # get room the client was in
            del adds[c] # remove client's address from list of connected clients
            del clients[c] # remove client from list of connected clients
            del rooms[c] # remove client's room from list of open rooms
            cons.remove(c) # remove client from list of sockets
            broadcast(bytes("%s has left the chat." % name, "utf8"), exit_room)
            break # stop handling this client
        
        elif cmsg == bytes("{help}","utf8"): # client looks for help
            c.send(bytes("Type '{users}' to see all users in this room.", "utf8"))
            c.send(bytes("Type '{exit}' to leave. ", "utf8"))
            c.send(bytes("Type '{room}' to see all rooms.", "utf8")) 
        
        elif cmsg == bytes("{users}", "utf8"): # client wants a list of users in this room
            users = ""
            for u in rooms: # iterate through all rooms
                if rooms[c] == rooms[u]: # if the user is in the current room
                    users += (clients[u] + " ") # add them to the string
            
            c.send(bytes("Users in this room are: " + users, "utf8"))
        
        elif cmsg == bytes("{room}", "utf8"): # client wants a list of all active rooms
            c.send(bytes("You are in the room: " + rooms[c], "utf8"))

        else: # client sent a normal message
            broadcast(cmsg, rooms[c], name + ": ") # add client name before broadcasting message

# function to send message to all connected clients
def broadcast(msg, room, prefix = ""):

    for c in rooms: # iterate through all rooms
        if rooms[c] == room: # if the client is in that room
            c.send(bytes(prefix, "utf8") + msg) # send message to all relevant clients

# function to gracefully terminate all connected clients
def terminate():
    for i in cons:
        i.send(bytes("Server has been terminated. Closing connection ...", "utf8"))
        i.close() # close socket
    SERVER.close()

# function to check for termination
def term_loop():
    cmd = input("\nType {done} to terminate server: ")

    if (cmd == "{done}"):
        terminate()

# variable declarations
cons = [] # list of sockets
clients = {} # empty set array for clients
adds = {} # empty set array for client addresses
rooms = {} # empty set array for tracking which rooms clients are in

HOST = "0.0.0.0" # IP of host 52.207.0.111
PORT = 7777 # port number
BUFFER = 1024 # buffer size
ADDRESS = (HOST, PORT) # address of server

SERVER = socket(AF_INET, SOCK_STREAM) # create server and open a socket
SERVER.bind(ADDRESS) # bind server to this address

# main function
if __name__ == "__main__":
    
    SERVER.listen(5)
    print("Waiting for connections ...")

    # create and manage threads for the server
    ACCEPT_THREAD = Thread(target=accept_connection)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()