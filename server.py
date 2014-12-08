#
# server.py - 
#

from constants import *
from socket import *
from socketwrappers import open_listensocket
import threading as th
import time, select, sys

gst_count = 0

class ChatServer(object):
    def __init__(self, port=8000):
        self.port = port
        self.domain = getfqdn()
        self.ip = gethostbyname(self.domain)
        self.listening = False
        self.clients = []

    def run(self):
        self.listening = True
        server = open_listensocket(self.ip, self.port)
        if dbg: print "listening on %s:%d" % (self.ip, self.port)
        inputs = [server]
        while self.listening:

            inputready, opr, excr = select.select(inputs, [], [], 1)
            for s in inputready:
               if s == server:
                   client = ClientThread(s.accept())
                   if dbg: print "Accepted connection from", addr
                   client.start()
                   self.clients.append(client)

        server.close()

    def stop(self):
        self.listening = False

class ClientThread(th.Thread):
    def __init__(self, socket, addr):
        data = conn.recv(1024)
        if data.startswith("Name:"):
            self.name = data.strip("GuestName:")
        else:
            self.name = "Guest%03d" % gst_count
            gst_count += 1

server = ChatServer()

def runserver():
    server.run()

def _test():
    thread = th.Thread(target=runserver)
    thread.start()
    print "what up"
    for _ in xrange(5):
        time.sleep(0.5)
        print "yup"
    server.stop()
    thread.join()

if __name__ == "__main__":
    _test()