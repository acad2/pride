import os
import hashlib

import mpre.network

NULL_RECEIVED = ["None"]

class Reliable_Udp(mpre.network.Udp_Socket):
    
    defaults = mpre.network.Udp_Socket.defaults.copy()
    defaults.update({"hash_function_name" : "sha1"})
    
    def __init__(self, **kwargs):
        self.sent, self.received, self.response_to = {}, {}, {}
        super(Reliable_Udp, self).__init__(**kwargs)
        _hash = self.hash_function = getattr(hashlib, self.hash_function_name)        
        self._packet_id_size = _hash('').digestsize
        self._new_conversation = #
        
    def sendto(self, data, target):
        if target[0] == "localhost":
            target = ("127.0.0.1", target[1])
        response_to_packet = self.received.get(target, NULL_RECEIVED)[-1]
        packet_id, packet = self.make_packet(data, response_to_packet)
        print
        self.alert("Sending packet id {}", [packet_id], level=0)
        self.socket.sendto(packet, target)
        self.sent[packet_id] = (packet, target)
        
    def make_packet(self, data, response_to, flags=' '):
        packet = response_to + flags + ' ' + data
        packet_id = self.hash_function((packet + os.urandom(64) if response_to == "None" else
                                                 response_to)).digest()
        return (packet_id, packet_id + packet)
        
    def recvfrom(self, network_packet_size):
        data, address = super(Reliable_Udp, self).recvfrom(network_packet_size)
        #print data, address
        self.alert("Received data from {}", [address], level=0)
        packet_id = data[:self.packet_id_size]
        response_to = data[
        packet_id, response_to, flags, data = data.split(" ", 3)
        print "Packet id: {}".format(packet_id)
        print "Response to id: {}".format(response_to)
        # flags = dont_reply, repeat_count
        
        if response_to not in self.sent:
            # remote machine is responding to a packet self did not send            
            
            if response_to == "None":
                self.alert("Starting a new conversation", level=0)
                # a new conversation
                try:
                    self.received[address].append(packet_id)
                except KeyError:
                    self.received[address] = [packet_id]
                    
            elif address in self.received:
                self.alert("No record of conversation", level=0)
                # a message in the middle of a conversation that i have no record of 
                #self.alert("Received a packet from a host
                pass
            else:
                self.alert("Idek", level=0)
                # not a new conversation, not a conversation I recognize, and i've never talked
                # to you before
                pass
            
        else:
            self.alert("Received response to message successfully", level=0)
            # everything should be in order; message was sent and response received
            del self.sent[response_to]
        print "payload: ", data    
        return data
        
def test():
    udp = components["Metapython"].create(Reliable_Udp, port=1337)
    udp2 = components["Metapython"].create(Reliable_Udp, port=1338)
    udp2.sendto("This is a test message", ("localhost", 1337))
    Instruction("Reliable_Udp", "sendto", "Response to your test message!", 
                                          ("localhost", 1338)).execute(priority=.2)
   # Instruction("Reliable_Udp1", "sendto", "Response to your response!",
   #                                        ("localhost", 1337)).execute(priority=.4)
if __name__ == "__main__":
    test()