#include "thread.h"
#include "socket.h"
#include <iostream>
#include <stdlib.h>
#include <time.h>

using namespace Sync;
class ClientThread : public Thread
{
    private:
        Socket& socket;
        ByteArray data;
    public: 
        bool running = true;
        ClientThread(Socket& socket) 
        : socket(socket)
        {}

        virtual long ThreadMain()
        {
            socket.Open();

            std::string input = "";
            std::cout << "Please input your data, or type 'done' to quit: ";
            std::cin >> input;
            std::cin.ignore();
            std::cout.flush();

            data = ByteArray(input);

			if (input == "done")
			{
				std::cout << "Terminating client..." << std::endl; // termination message
				running = false; // client is no longer active
				break; // exit client
			}

            try{
                socket.Write(data);
                socket.Read(data);
                std::cout << "Server Response: " << data.ToString() << std::endl; // output data from server
			}
			catch (...) // if the operation fails
			{
				std::cout << "Error accessing socket from client!" << std::endl; 
			}
		    return 0; // exit function with all clear
		}
};

int main(void)
{
    std::cout << "SE3313 Final Project" << std::endl;
    
    Socket socket("127.0.0.1", 3000);
    ClientThread clientThread(socket);
    while(clientThread.running == true)
    {
        sleep(1);
    }

    socket.close();

    return 0;
}