from socket import *

if __name__ == "__main__":
    receiver = socket(AF_INET, SOCK_STREAM)
    receiver.bind(("0.0.0.0", 40021))
    receiver.listen(1)
    f = open("audiofli.wav", "wb")
    connection, _from = receiver.accept()
    downloading = True
    print "downloading"
    while downloading:
        data = connection.recv(4096)
    
        if not data:
            downloading = False
    
        f.write(data)
        f.flush()
    print "finished"
