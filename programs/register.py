import mpre.base
import mpre.errors

class Registration(mpre.base.Base):
    
    defaults = mpre.base.Base.defaults.copy()
    defaults.update({"service_type" : "mpre._metapython.Shell",
                     "host_info" : tuple(),
                     "username" : '',
                     "password" : '',
                     "parse_args" : True})
    
    def __init__(self, **kwargs):
        super(Registration, self).__init__(**kwargs)
        username = self.username or mpre.userinput.get_user_input("Please provide a username: ")
                            
        self.client = self.create(self.service_type, username=username, password=self.password,
                                  host_info=self.host_info, auto_login=False)
        host_string = '' if not self.host_info else "@ {}".format(self.host_info)
        self.alert("Attempting to register with {} {}".format(self.service_type, host_string))
        self.client.register()        
        
if __name__ == "__main__":
    registration = Registration()