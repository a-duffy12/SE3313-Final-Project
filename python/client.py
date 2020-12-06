from socket import *
from threading import Thread
import tkinter

# function to receive messages
def rec():

    while True:
        
        try:
            msg = client_socket.recv(BUFFER).decode("utf8") # decode incoming message
            msgs.insert(tkinter.END, msg) # add message to list of messages
        
        except OSError: # if client has left the chat
            break

# function to send a message
def send(event=None): 

    msg = new_msg.get() # next message to send is retreived from client input
    new_msg.set("") # erases input so client can send another message
    client_socket.send(bytes(msg, "utf8")) # send message

    if msg == "{exit}": # client wants to leave chat room
        client_socket.close() # close client socket
        top.quit() # exit tkinter

# function to close connection when closing GUI
def close_process(event=None):

    new_msg.set("{exit}") # set value of message to be 'exit'
    send() # send message

# tkinter variable declaration
top = tkinter.Tk()
top.title("SE3313 Chat App")

frame = tkinter.Frame(top) # create GUI frame for message
new_msg = tkinter.StringVar() # get input for messages to send
new_msg.set("Type message here")
scrollbar = tkinter.Scrollbar(frame) # can scroll along the frame

msgs = tkinter.Listbox(frame, height=15, width=50, yscrollcommand=scrollbar.set) # set scrollbar parameters

# pack all tkinter objects
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msgs.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msgs.pack()
frame.pack()

# create fields to type text
input_field = tkinter.Entry(top, textvariable=new_msg) # establish what variable gets updated with input
input_field.bind("<Return>", send) # bind field to send function
input_field.pack()
send_button = tkinter.Button(top, text="Send", command=send) # create a button to send the message
send_button.pack()

top.protocol("WM_DELETE_WINDOW", close_process) # set protocol for exiting

# client variable declaration
HOST = input("Enter host address: ")
PORT = input("Enter port number: ")

if not HOST: # if a host is not specified, set it to 52.207.0.111
    HOST = "localhost"

if PORT: # if a port is not specified, set it to 7777
    PORT = int(PORT) # take port and turn it into an integer
else:
    PORT = 7777

BUFFER = 1024 # buffer sizw
ADDRESS = (HOST, PORT) # address of server to connect to

client_socket = socket(AF_INET, SOCK_STREAM) # create a socket for the client to use
client_socket.connect(ADDRESS) # connect to server

# create and manage a thread for the client
rec_thread = Thread(target=rec)
rec_thread.start()

tkinter.mainloop() # start GUI