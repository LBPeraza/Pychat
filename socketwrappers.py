#
# socketwrappers.py
#

from socket import *

def open_clientsocket(host, port):
    for res in getaddrinfo(host, port):
        af, socktype, proto, canonname, sa = res
        try:
            s = socket(af, socktype, proto)
        except:
            s = None
            continue
        try:
            s.connect(sa)
        except:
            s.close()
            s = None
            continue
        break
    if s == None:
        return -1
    return s

def open_listensocket(host, port):
    ainfo = getaddrinfo(host, port)
    for res in ainfo:
        af, socktype, proto, canonname, sa = res
        try:
            s = socket(af, socktype, proto)
        except:
            s = None
            continue
        try:
            s.bind(sa)
            s.listen(1)
        except:
            s.close()
            s = None
            continue
        break
    if s == None:
        return -1
    return s