#!/usr/bin/env python3

import socketserver

class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def setup(self):
        print("Connected.")
    
    def finish(self):
        print("Disconnected.")

    def handle(self):
        # self.request is the TCP socket connected to the client
        while True:
            print(self.request.recv(1024).strip().decode())

if __name__ == "__main__":
    HOST, PORT = "localhost", 9000

    # Create the server, binding to localhost on port 9999
    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        print("Listening on 127.0.0.1:9000...")
        server.serve_forever()
