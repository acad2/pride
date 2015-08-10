import mpre.network as network


class Tcp_Service_Proxy(network.Server):

    def __init__(self, **kwargs):
        super(Tcp_Service_Proxy, self).__init__(**kwargs)
        self.Tcp_Socket_type = Proxy_Client
                
    def on_connect(self, connection):
        pass
        
        
class Proxy_Client(network.Tcp_Socket):
    
    def __init__(self, **kwargs):
        super(Proxy_Client, self).__init__(**kwargs)
        
    def recv(self):
        request = self.wrapped_object.recv(self.network_packet_size)        
        service_name, command, value = request.split(" ", 2)
        self.respond_with(self.reply)
        request = command + " " + value
        self.reaction(service_name, request)
              
    def reply(self, sender, packet):
        self.send(str(sender) + " " + packet)

                           
"""
class Tcp_Service_Test(network.Tcp_Client):
    
    def on_connect(self):        
        self.send("File_Service get_filesize base.py")
                           
    def recv(self):
        self.network_buffer += self.socket.recv(self.network_packet_size)
"""
        
        
layer_map = {(x, [cached_layer, draw_method]) for x in xrange(60)}

renderer.blit(layer_map[cached_layer_level][0]
for z in xrange(cached_layer_level + 1, max_layers):
    renderer.blit(layer_however)
        
        
class Struct(object):
   
    format_switch = {int : 'q',
                     float : 'd',
                     str : 's',
                     bool : '?'}
    
    format_size = {'q' : 8,
                   'd' : 8,
                   's' : 0,
                   '?' : 1}
                      
    def __init__(self, dictionary):
        self.dictionary = dictionary
        _struct = self.struct = self.create_struct(dictionary)
        self.packed_values = _struct.pack(*self.values)
        
    def byte_representation(self, dictionary):
        (total_size,
         size_string,
         packed_data,
         self.struct,
         self.struct_slice,
         self.unpacked_index,
         self.byte_offsets,
         self.attribute_order,
         self.is_pickled) = self.from_dictionary(dictionary)
        
        return size_string + packed_data
        
    def from_dictionary(self, dictionary):
        (byte_offsets,
         unpacked_index,
         attribute_order, 
         values, 
         _struct,
         is_pickled) = self.create_struct(dictionary)
                 
        total_size = _struct.size
        struct_slice = slice(0, total_size)
        return (total_size, _struct.pack(*values),
                _struct, struct_slice,  unpacked_index, byte_offsets,
                attribute_order, is_pickled)
                                                                       
    def pack(self, value):
        format_character = Struct.format_switch.get(type(value), "pyobject")
        if format_character is "pyobject":
        #    print "PICKLING: ", type(value), value
            value = pickle.dumps(value)
            format_size = len(value)
            format_character = str(format_size) + 's'  
            is_pickled = True
        else:
            format_size = Struct.format_size[format_character]
            if not format_size:
                format_size = len(value)
                format_character = str(format_size) + format_character
            is_pickled = False
            
       # print "packed {} into {}".format(value, format_character)
        return format_size, format_character, value, is_pickled
        
    def create_struct(self, dictionary):        
        struct_layout = ''
        
        unpacked_index = self.unpacked_index = {}
        attribute_byte_offset = self.attribute_byte_offset = {}
        is_pickled = self.is_pickled = {}
        attribute_order = self.attribute_order = []
        values = self.values = []
        
        index_count = 0
        byte_index = 0
        for key, value in dictionary.items():
            attribute_order.append(key)
            unpacked_index[key] = index_count
            format_size, format_character, value, pickled_flag = self.pack(value)
            
            values.append(value)
            attribute_byte_offset[key] = byte_index, byte_index + format_size
            is_pickled[key] = pickled_flag
            
            index_count += 1            
            struct_layout += format_character
            byte_index += format_size
                                           
        return struct.Struct(struct_layout)                        