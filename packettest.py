import mpre
import mpre.networkssl

def packetize_send(send):
    def _send(self, data):
        return send(self, str(len(data)) + ' ' + data)   
    return _send
    
def packetize_recv(recv):
    def _recv(self, buffer_size=0):
        data = recv(self, buffer_size)
        packets = []
        while data:
            try:
                packet_size, data = data.split(' ', 1)
            except ValueError:
                self._old_data = data
                break
            packet_size = int(packet_size)
            packets.append(data[:packet_size])
            data = data[packet_size:]   
        print "Received packets: ", packets
        return packets    
    return _recv
    
class Packet_Client(mpre.networkssl.SSL_Client):
            
    defaults = mpre.networkssl.SSL_Client.defaults.copy()
    defaults.update({"_old_data" : bytes()})
    
    @packetize_send
    def send(self, data):
        return super(Packet_Client, self).send(data)
    
    @packetize_recv
    def recv(self, buffer_size=0):
        return super(Packet_Client, self).recv(buffer_size)      
        
        
class Packet_Socket(mpre.networkssl.SSL_Socket):
            
    defaults = mpre.networkssl.SSL_Socket.defaults.copy()
    defaults.update({"_old_data" : bytes()})
    
    @packetize_send
    def send(self, data):
        return super(Packet_Socket, self).send(data)
    
    @packetize_recv
    def recv(self, buffer_size=0):        
        return super(Packet_Socket, self).recv(buffer_size)
                       
            
class Packet_Server(mpre.networkssl.SSL_Server):
    
    defaults = mpre.networkssl.SSL_Server.defaults.copy()
    defaults.update({"Tcp_Socket_type" : Packet_Socket})
    
    

if __name__ == "__main__":
    mpre.objects["Metapython"].create("mpre._metapython.Shell", username="localhost")
    server = Packet_Server(port=40033)
    client = Packet_Client(target=("localhost", 40033))
    