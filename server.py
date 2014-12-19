#
# server.py - 
#

from constants import *
from socket import *
from socketwrappers import open_listensocket
import threading as th
import time, select, sys, mutex

gst_count = 0

class ChatServer(object):
    def __init__(self, port=8000):
        self.port = port
        self.domain = getfqdn()
        self.ip = gethostbyname(self.domain)
        self.listening = False
        self.clients = []

    def listen(self):
        quitters = []
        showclients = False
        i = 0
        while i < len(self.clients):
            client = self.clients[i]
            if not client.running:
                quitters.append(client.username)
                self.clients.pop(i)
                client.join()
            else:
                i += 1
                for flag in client.flags:
                    if flag == "showclients":
                        showclients = True
                client.flags = []

        if showclients:
            print self.clients

        inputready, opr, excr = select.select([self.server], [], [], 0)
        for s in inputready:
            if s == self.server:
                acpt = socket, addr = s.accept()
                client = ClientThread(acpt)
                print "Accepted connection from", addr
                if client.username:
                    client.start()
                    self.clients.append(client)
                else:
                    client.socket.close()
                    del client


    def run(self):
        self.listening = True
        self.server = open_listensocket(self.ip, self.port)
        print "listening on %s:%d" % (self.ip, self.port)
        while self.listening:

            self.listen()

        for client in self.clients():
            client.socket.send("\r\nkick")
            client.running = False
            client.join()
        self.server.close()

    def stop(self):
        print self.listening
        self.listening = False

    def send_message(self, user, message):
        for cl in self.clients:
            if cl.username != user:
                cl.send_message(message)

class ClientThread(th.Thread):
    def __repr__(self):
        return "User: %s" % self.username

    def __init__(self, (socket, addr)):
        run = lambda: self.run()
        super(ClientThread, self).__init__(target=self.run)
        data = socket.recv(1024)
        if data.startswith("UserName:"):
            self.username = data.lstrip("UserName:")
            self.running = True
        else:
            self.username = None
            self.running = False
            socket.send("That's pretty rude :(")
        self.socket = socket
        self.address = addr
        self.buf = ""
        self.mut = mutex.mutex()
        self.flags = []

    def run(self):
        def send_buf(x):
            self.socket.send(self.buf)
            self.buf = ""
            self.mut.unlock()
        while self.running:
            data = self.socket.recv(1024)
            if data == "\r\t:::quitting:::":
                self.running = False
            elif data == "clientlist":
                self.flags = ['showclients']
            self.mut.lock(send_buf, None)
        self.socket.close()

    def send_message(self, message):
        def add_to_buf(message):
            self.buf += message
            self.mut.unlock()

        self.mut.lock(add_to_buf, message)
