#@192.168.1.240:Instruction(component_name, method, *args, **kwargs) in 10.00 with instruction_callback and local_callback
#
## preprocesses to:
#rpc_sessions[ip_address].execute(Instruction("->Python->Interpreter", "execute_instruction", 
#                                             instruction, priority, 
#                                             instruction_callback), local_callback)
#
import pride.importers

def handle_input(source):
    current_index = 0
    while '@' in source[current_index:]:
        indices = pride.importers.Parser.find_symbol('@', source[current_index:], False, False)
        if not indices:
            break
        start, end = indices[0]
        current_index = end
        colon = source.index(':', current_index)
        try:
            is_decorator = source.index('\n', current_index) < colon
        except ValueError:
            is_decorator = False
        if not is_decorator: 
            name = source[end:colon]
            replacement = "pride.rpc_sessions[{}].execute('->Python->Interpreter', 'execute_instruction', ".format(name)
                    
            source = ''.join((source[:start], replacement,
                              source[colon + 1:].replace(" in ", ', ', 1).replace(" with ", ', ', 1).replace(" and ", ', ', 1),
                              ')'))        
    return source
        
            
class Device_Manager(pride.authentication.Authenticated_Service):
    
    def __init__(self, **kwargs):
        super(Device_Manager, self).__init__(**kwargs)
        for device_type in self.default_devices:
            self.create(device_type)
            
            
class IoT_Device(pride.base.Base): pass
            
        
if __name__ == "__main__":
    test = "@door:unlock in 0 with alert and notify"
    print "\nWith macro:"
    print test
    print "\nAfter expansion: "
    print handle_input(test)