import os
import collections
import hmac
import getpass
import hashlib
import sqlite3
import pickle
import traceback

import pride
import pride.base as base
import pride.network as network
import pride.fileio as fileio
from pride.datastructures import Latency, timestamp
Instruction = pride.Instruction
#objects = pride.objects
           
class Network_Service(network.Udp_Socket):
    
    """ Reliable udp socket; under development"""
    defaults = network.Udp_Socket.defaults.copy()
    
    end_request_errors = {"0" : "Invalid Request"}
    
    def __init__(self, **kwargs):
        super(Network_Service, self).__init__(**kwargs)
        self.expecting_response = collections.deque(maxlen=20)
        self.received = collections.deque(maxlen=20)
        self.packet_cache = collections.deque(maxlen=20)
        self._return_to = {}
        self.sent_at = {}
        self.resent = set()

    def socket_recv(self):
        packet, sender = self.recvfrom(self.network_packet_size)

        # (hopefully) reliable udp mechanisms
        id, response_to, data = packet.split(" ", 2)     
        self.received.append(response_to)
        request = (sender, response_to)
        
        self.alert("Checking to see if {} is expected",
                   [request],
                   level='vv')    
        try:                   
            self.expecting_response.remove(request)
        except ValueError:
            if response_to == "None":
                self.alert("Received a new connection {}",
                           [id],
                           'vv')
            else:
                self.alert("Received duplicate packet {}",
                           [id],
                           level='vv')
                if request in self.resent:
                    self.resent.remove(request)  
                else:
                    return
        
        # packet parsing
        end_of_request = False
        if response_to in self._return_to:
            command = self._return_to[response_to]
            value = data
            if value[:11] == "end_request":
                value = value[11:]
                end_of_request = True
        else:
            if data[:11] == "end_request":
                data = data[12:]
                end_of_request = True
            try:
                command, value = data.split(" ", 1)
            except ValueError:
                if not end_of_request: # malformed request
                    response = self.invalid_request(sender, packet)
                    self.send_data(response, sender, response_to, False)  
                    return

        if end_of_request:
            self.alert("Request finished {}",
                       [request],
                       'vv')
            return
            
        self.alert("handling response {} {}",
                   [command, value[:32]],
                   level='vv')
        #print "reaction: ", self.reference, command, value[:45]
        response = getattr(self, command)(sender, value)
        response = response if response else "end_request"
        expect_response = response[:11] != "end_request"
        
        self.alert("Sending response: {} in response to {}",
                   [response, id],
                   level='vvv')
        self.send_data(response, sender, response_to, expect_response)
        
        #self._handle_resends()
        
    def send_data(self, data, to=None, 
                  response_to='None', expect_response=True):
        reaction = ''
        lowercase_data = data.lower()
        
        if lowercase_data[:6] == "return":
            flag, reaction, data = data.split(" ", 2)
        
        id, packet = self._make_packet(response_to, data)
        
        if reaction:
            self._return_to[id] = reaction
            
        if to[0] == "localhost":
            to = ("127.0.0.1", to[1])                            
        
        self.sendto(packet, to)
        
        if expect_response:
            self.expecting_response.append((to, id))
            
        self.packet_cache.append((id, packet))
        self.sent_at[id] = timestamp()
        self.alert("sent packet {} {} to {} in response to {}",
                   [id, data[:32], to, response_to],
                   level='vv')                               
        
    def _handle_resends(self):
        packet_cache = dict((id, packet) for id, packet in self.packet_cache)
        sent_at = self.sent_at
        resend_after = .2
        
        for target, id in self.expecting_response:
            if timestamp() - sent_at[id] > resend_after:
                packet = packet_cache[id]
                
                self.alert("Resending {}", [id], level=0)
                        
                objects["Network"].send(self, packet, target)
                self.resent.add((target, id))               
               
    def invalid_request(self, sender, packet):
        self.alert("Invalid reaction request\nFrom:{}\nPacket:{}",
                   [sender, packet],
                   level=0)
                                    
        return "end_request invalid_request " + packet
    
    def _make_packet(self, response_to, data):
        message = response_to + " " + data
        id = str(hash(message))
        return id, id + " " + message
        
    def demo_reaction(self, sender, packet):
        print "im a demo reaction for", sender, packet
        counter = int(packet)
        if counter >= 1000:
            print "1000 reactions happened between {} and {}".format(self, sender)
            response = ''
        else:
            response = "demo_reaction " + str(counter + 1)
        return response
        
                      
if __name__ == "__main__":
    from pride.tests.network2 import test_file_service, test_authentication, test_proxy, test_reliability
   # test_reliability()
   # test_authentication()
   # test_file_service()
   # test_rpc()    