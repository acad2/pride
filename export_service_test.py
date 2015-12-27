import pride

class Export_Service(pride.base.Base):
        
    defaults = {"client_type" : "pride.interpreter.Shell"}
    mutable_defaults = {"connections" : dict}
    
    def export_to(self, ip, module_source, as_name):
        if ip not in self.connections:
            client = self.create(self.client_type, ip=ip, startup_definitions=module_source)
            self.connections[ip] = client
        else:
            self.connections[ip].handle_input(module_source)