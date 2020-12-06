#include "Semaphore.h"
#include "socketserver.h"
#include "thread.h"
#include <algorithm>
#include <list>
#include <stdlib.h>
#include <thread>
#include <time.h>
#include <vector>

using namespace Sync;

// thread to create the socket
class SocketThread : public Thread
{
    private:
        Socket &socket; // socket the server offers
        ByteArray data; // bytearray to store incoming data from client
        int roomNum; // total number of chat rooms open
        int port; // port number server uses
        bool& terminate; // to track whether server should termiante or not
        std::vector<SocketThread*> &socketThreadPointers; // array to hold the socket threads

    public:
        
        // constructor 
        SocketThread(Socket& socket, std::vector<SocketThread*> &clientSocketThread, bool &terminate, int port) :
            socket(socket), socketThreadPointers(clientSocketThread), terminate(terminate), port(port)
        {}

        // destructor
        ~SocketThread()
        {
            this->terminationEvent.Wait(); // call graceful termination
        }

        // function to get the socket objects
        Socket& GetSocket()
        {
            return socket;
        }

        // function to get the current chat room number
        const int GetRoomNum()
        {
            return roomNum;
        }

        virtual long ThreadMain()
        {
            std::string portS = std::to_string(port); // get port number as a string
            Semaphore clientSem(stringPort); // each socket thread has a semaphore referencing the port in use

            try // try to read/write from socket
            {
                socket.Read(data); // read data from socket

                std::string chatData = data.ToString(); // get data from client
                chatData = chatData.substr(1, chatData.size() - 1); // unappend chat room number from client data
                roomNum = std::stoi(chatData); // get chat room number from chat data
                std::cout << "This is chat room " << roomNum << std::endl; // output chat room number

                while (!terminate) // as long as the server is active
                {
                    int result = socket.Read(data); // get result form reading the socket

                    if (result == 0) // if result is 0, then the client has closed the connection
                    {
                        break; // close socket connection
                    }

                    std::string recv = data.ToString(); // get byte message from client

                    if (recv == "done\n") 
                    {
                        clientSem.Wait(); // begin mutual exclusion

                        socketThreadPointers.erase(std::remove(socketThreadPointers.begin(), socketThreadPointers.end(), this), socketThreadPointers.end()); // find the current socket thread and delete it

                        clientSem.Signal(); // end mutual exclusion
                        break; // exit the server
                    }

                    if (recv[0] == "!") // ! indicates that the client is switching chat rooms
                    {
                        std::string chatMsg = recv.substr(1, recv.size() - 1); // get the message from the data

                        roomNum = std::stoi(chatMsg); // get chat room number from message
                        std::cout << "A client joined room " << roomNum << std::endl; // output client connection message
                        continue; // do not sever connection
                    }

                    clientSem.Wait(); // enter critical section
                    
                    for (int i = 0; i < socketThreadPointers.size(); i++) // iterate through all socket threads
                    {
                        SocketThread *clientSocketThread = socketThreadPointers[i]; // get client threads

                        if (clientSocketThread->GetRoomNum() == roomNum) // if the current room's thread is found
                        {
                            Socket &clientSocket = clientSocketThread->GetSocket(); // get client socket 
                            byteMsg = ByteArray(recv); // turn message into byte array
                            clientSocket.Write(byteMsg); // send byte array
                        }
                    }

                    clientSem.Signal(); // exit critical section
                }

                std::cout << "A client has left the server" << std::endl; // client exit message
            }
            catch(...) // if the operation fails
            {
                std::cout << "Error accessing socket from server!" << std::endl;
            }

            return 0; // exit with all clear
        }
};

// This thread handles the server operations
class ServerThread : public Thread
{

    private:
        SocketServer& server; // server object
        int roomNum; // total number of chat rooms open
        int port; // port number server uses
        bool& terminate; // to track whether server should termiante or not
        std::vector<SocketThread*> socketThreadPointers; // array to hold socket threads

    public:

        // constructor
        ServerThread(SocketServer& server, int roomNum, int port) :
        server(server), roomNum(roomNum), port(port)
        {}

        // destructor
        ~ServerThread()
        {
            for (auto thread : socketThreadPointers)
            {
                try
                {
                    Socket& soc = thread->GetSocket(); // get current socket
                    soc.Close(); // close current socket
                }
                catch(...)
                {
                    std::cout << "Error closing socket!" << std::end;
                }
                
            }

            std::vector<SocketThread*>().swap(socketThreadPointers);
            terminate = true;
        }

        virtual long ThreadMain()
        {
            while (true)
            {
                try
                {
                    std::string portS = std::to_string(port); // get port number as a string
                    Semaphore serverSem(portS, 1, true); // each server thread has a semaphore referencing the port in use

                    std::string chats = std::to_string(roomNum) + "\n"; // create string of chat messages with the room number
                    byteChats = ByteArray(chats); // get chat messages as a byte array

                    // Wait for a client socket connection
                    Socket soc = server.Accept(); // accept an incoming client connection
                    soc.Write(byteChats); // send all byte chat data 
                    Socket* newConnection = new Socket(soc); // create a new socket for this connection

                    // A reference to this pointer
                    Socket& socketReference = *newConnection; // get a reference to this new connection
                    socketThreadPointers.push_back(new SocketThread(socketReference, std::ref(socketThreadPointers), terminate, port)); // create a socket thread for this connection and add it to the array
                }
                catch()
                {
                    std::cout << "Error accepting client connection!" << std::endl;
                    return 1;
                }

            }

            return 0;
        }
};

int main(void)
{
    int port = 3000; // use port 3000
    int maxRooms = 12; // maximum number of rooms available at one time

    std::cout << "SE3313 Final Project Server" << std::endl;
    std::cout << "Hit 'ENTER' to terminate the server" << std::endl;

    // Create our server
    SocketServer server(port);

    // Need a thread to perform server operations
    ServerThread serverThread(server);

    // This will wait for input to shutdown the server
    FlexWait cinWaiter(1, stdin); // any input will initiate next step
    cinWaiter.Wait(); // wait for input
    std::cin.get();

    std::cout << "Terminating server..." << std::endl; // termination message

    // Shut down and clean up the server
    server.Shutdown(); // gracefully terminate the server
}