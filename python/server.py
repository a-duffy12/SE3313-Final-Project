# SE3313 Final Project Chat Server

from socket import *
from threading import Thread

# function to accept incoming connections
def accept_connection():
    
    while True:
        client, client_address = SERVER.accept() # get client and their address from incoming connection
        print("%s:%s has connected." % client_address)
        client.send(bytes("Type the name you wish to use and press 'ENTER'.", "utf8"))
        adds[client] = client_address # store client address in list
        Thread(target=handle, args=(client,)).start()

# function to handle client actions by taking in a client
def handle(c): 

    name = c.recv(BUFFER).decode("utf8") # get client's name
    wmsg = "Welcome %s. If you wish to leave, type {exit} to exit." % name # welcome message
    c.send(bytes(wmsg, "utf8")) # send welcome message
    gmsg = "%s has joined the chat." % name # global connection message
    broadcast(bytes(gmsg, "utf8")) # send global message
    clients[c] = name # add client to list of connected clients

    while True:
        cmsg = c.recv(BUFFER) # get client message
        if cmsg != bytes("{exit}", "utf8"): # as long as client is not exiting
            broadcast(cmsg, name+": ") # add client name before broadcasting message
        else:
            #c.send(bytes("{exit}", "utf8"))
            c.close() # close client connection
            del clients[c] # remove client from list of connected clients
            broadcast(bytes("%s has left the chat." % name, "utf8"))
            break # stop handling this client

# function to send message to all connected clients
def broadcast(msg, prefix = ""):

    for soc in clients:
        soc.send(bytes(prefix, "utf8") + msg) # send message to all relevant clients

# variable declarations
clients = {} # empty object array for clients
adds = {} # empty object array for client addresses

HOST = "" # IP of host 52.207.0.111
PORT = 7777 # port number
BUFFER = 1024 # buffer size
ADDRESS = (HOST, PORT) # address of server

SERVER = socket(AF_INET, SOCK_STREAM) # create server and open a socket
SERVER.bind(ADDRESS) # bind server to this address

# main function
if __name__ == "__main__":
    
    SERVER.listen(5)
    print("Waiting for connections ...")

    # create and manage a thread for the server
    ACCEPT_THREAD = Thread(target=accept_connection)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()