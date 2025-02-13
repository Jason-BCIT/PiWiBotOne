import os
import socket
import network
import websocket_helper
from time import sleep
from ws_connection import WebSocketConnection, ClientClosedError

class WebSocketClient:
    def __init__(self, conn):
        print("WebSocketClient.__init__ in ws_server.py")
        self.connection = conn

    def process(self):
        print("WebSocketClient.process in ws_server.py");
        pass

class WebSocketServer:
    def __init__(self, page, max_connections=1):
        self._listen_s = None
        self._clients = []
        self._max_connections = max_connections
        self._page = page

    def _setup_conn(self, port, accept_handler):
        self._listen_s = socket.socket()
        self._listen_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        ai = socket.getaddrinfo("0.0.0.0", port)
        addr = ai[0][4]

        self._listen_s.bind(addr)
        self._listen_s.listen(1)
        if accept_handler:
            self._listen_s.setsockopt(socket.SOL_SOCKET, 20, accept_handler)
        for i in (network.AP_IF, network.STA_IF):
            iface = network.WLAN(i)
            if iface.active():
                print("WebSocket started on ws://%s:%d" % (iface.ifconfig()[0], port))

    def _accept_conn(self, listen_sock):
        print("listen_sock=",listen_sock)
        listen_sock.settimeout(3)
        try:
            cl, remote_addr = listen_sock.accept()
        except:
            print("Socket timed out");
        print("Client connection from:", remote_addr)
        
        
        if len(self._clients) >= self._max_connections:
            # Maximum connections limit reached
            cl.setblocking(True)
            print("Going to say too many connections.")
            cl.sendall("HTTP/1.1 503 Too many connections\n\n")
            print("Too many connections.")
            cl.sendall("\n")
            print("Now going to sleep and close.")
            #TODO: Make sure the data is sent before closing
            sleep(0.1)
            cl.close()
            print("now returning")
            return

        try:
            websocket_helper.server_handshake(cl)
        except OSError:
            # Not a websocket connection, serve webpage
            self._serve_page(cl)
            return

        self._clients.append(self._make_client(WebSocketConnection(remote_addr, cl, self.remove_connection)))

    def _make_client(self, conn):
        print("_make_client in ws_server.py")
        return WebSocketClient(conn)

    def _serve_page(self, sock):
        try:
            print("_serve_page in ws_server.py")
            sock.sendall('HTTP/1.1 200 OK\nConnection: close\nServer: WebSocket Server\nContent-Type: text/html\n')
            length = os.stat(self._page)[6]
            sock.sendall('Content-Length: {}\n\n'.format(length))
            # Process page by lines to avoid large strings
            with open(self._page, 'r') as f:
                for line in f:
                    sock.sendall(line)
        except OSError:
            # Error while serving webpage
            print("Exception OSError in ws_server.py _serve_page")
            pass
        sock.close()

    def stop(self):
        if self._listen_s:
            self._listen_s.close()
        self._listen_s = None
        for client in self._clients:
            client.connection.close()
        print("Stopped WebSocket server.")

    def start(self, port=80):
        if self._listen_s:
            self.stop()
        self._setup_conn(port, self._accept_conn)
        print("Started WebSocket server.")

    def process_all(self):
        for client in self._clients:
            client.process()

    def remove_connection(self, conn):
        print("remove_connection in ws_server.py")
        for client in self._clients:
            if client.connection is conn:
                self._clients.remove(client)
                return