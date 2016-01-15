import pride.network
import pride.vmlibrary

class Tcp_Port_Tester(pride.network.Tcp_Client):
    
    def on_connect(self):
        super(Tcp_Port_Tester, self).on_connect()
        self.parent.host_discovered(self.peername)
        self.delete()   
        
        
class Scanner(pride.vmlibrary.Process):

    defaults = {"subnet" : "127.0.0.1", "ports" : (22, ),
                "range" : (0, 0, 0, 255), "yield_interval" : 100}

    mutable_defaults = {"discovered_hosts" : list}
    
    verbosity = {"host_discovered" : 'v', "port_open" : 'v', "next_address" : 'vv',
                 "finished" : "vv"}
    
    def __init__(self, **kwargs):
        super(Scanner, self).__init__(**kwargs)
        self.thread = self.new_thread()
        
    def run(self):
        try:
            next(self.thread)
        except StopIteration:
            self.alert("Finished launching connections for scan",
                       level=self.verbosity["finished"])
            self.running = False

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
                        self.alert("Scanning address: {}", [address], 
                                   level=self.verbosity["next_address"])
                        for port in ports:                            
                            self.create(Tcp_Port_Tester, host_info=(address, port))
                            yield_interval -= 1
                            if not yield_interval:
                                yield
                                yield_interval = self.yield_interval

    def host_discovered(self, address):
        if address[0] not in self.discovered_hosts:
            self.discovered_hosts.append(address)
            self.alert("Discovered a host at {}:{}", address, 
                       level=self.verbosity["host_discovered"])
        self.alert("Found a service at {}:{}", address, 
                   level=self.verbosity["port_open"])