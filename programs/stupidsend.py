from socket import *
from sys import argv

if __name__ == "__main__":
    filename = argv[1]
    
    sender = socket(AF_INET, SOCK_STREAM)
    sender.connect(("192.168.1.240", 40021))
    print "connected"
    f = open(filename, "rb")
    data = f.read()
    f.close()
    print len(data)
    while data:
        sender.send(data[:4096])
        data = data[4096:]
        print len(data), "remaining"
    print "finished"
