import mpre.networklibrary as networklibrary
import mpre.defaults as defaults
import mpre.base as base
Instruction = base.Instruction

class File_Service(networklibrary.UDP_Socket):

    defaults = defaults.File_Service

    def __init__(self, **kwargs):
        super(File_Service, self).__init__(**kwargs)     
                                          

class Download(networklibrary.UDP_Socket):
    
    defaults = defaults.Download
    
    def __init__(self, **kwargs):
        super(Download, self).__init__(**kwargs)
        self.file = self.create("iolibrary.File", self.filename, 'wb')
        
        request = self.make_request()
        self.public_method("Asynchronous_Network", "buffer_data", connection, request, self.target)
           
    def socket_send(self, connection, data):
        connection.send(data)
        
    def make_request(self):
        packet_size = self.network_packet_size
        request_size = min(self.data_remaining, network_packet_size)
        file_position = self.file.tell()
        
        file_request = "{} {} {}".format(self.filename, 
                                         file_position, 
                                         file_position + network_packet_size)
        return "{} {}".format(len(file_request), file_request)        
        
    def socket_recv(self, connection):
        incoming_packet, address = connection.recvfrom(self.network_packet_size)
        
        packet = self.leftover_packet + incoming_packet
        file_data, remaining_responses = self.handle_response(packet)
        
        while file_data:
            self.record_response(file_data)
            file_data, remaining_responses = self.handle_response(remaining_responses)
        
        self.leftover_packet = remaining_responses        
            
    def handle_response(self, packet):
        try:
            header, remaining_data = packet.split(" ", 1)
        except ValueError:
            file_data, remaining_responses = None, packet
        else: 
            message_size = int(header)
            if message_size < 0: # beginning of message!
                self.remaining = self.file_size = -message_size
                file_data, remaining_responses = self.handle_response(remaining_data)
            
            else:
                file_data = remaining_data[:message_size]
                remaining_responses = remaining_data[message_size:]
                self.remaining -= message_size
                
        return file_data, remaining_responses
                        
    def record_response(self, response):
        self.file.write(response)
        
        if self.remaining:
            request_size = self.network_packet_size
            self.public_method("Asynchronous_Network", "buffer_data", 
                               "{} {} {};".format(self.filename, self.file.tell(), request_size))
                           

class File_Server(networklibrary.UDP_Socket):
                            
    defaults = defaults.Upload
    
    def __init__(self, **kwargs):
        super(File_Server, self).__init__(**kwargs)  
        
    def socket_recv(self, connection):
        original_request, address = connection.recvfrom(self.network_packet_size)
        
        response, other_requests = self.handle_request(original_request, address)
        while response: # if check and setup look in one move
            self.public_method("Asynchronous_Network", "buffer_data",
                               connection, response, address)        
            response, other_requests = self.handle_request(other_requests, address)
        assert not other_requests
        #self.data = other_requests            
        
    def socket_send(self, connection, data, to):
        connection.sendto(data, to)
        
    def handle_request(self, request, address):
        try:
            packet_size, remaining_data = request.split(" ", 1)
        except ValueError:
            response, other_requests = None, request
        else: 
            message_size = int(packet_size)
            filename, start_from, request_size = remaining_data[:message_size].split()
            response = self.make_response(filename, start_from, request_size)
            other_requests = remaining_data[message_size:]
           
        return response, other_requests
      
    def make_response(self, filename, start_from, request_size):        
        if request_size >= self.mmap_threshold:
            _file, offset = self.public_method("IO_Manager", "load_mmap", filename, start_from)
            data = _file[offset:offset + request_size]
        else:
            _file = self.files[filename] if filename in self.files else\
                    self.create(File, filename, 'rb')
            _file.seek(start_from)
            data = _file.read(request_size)
        return len(data) + " " + data
        
if __name__ == "__main__":
    Instruction("Asynchronous_Network", "create", File_Server).execute()
    Instruction("System", "create", Download, target=("localhost", 40021)).execute()