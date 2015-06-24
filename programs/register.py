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
        if not self.username:
            raise mpre.errors.ArgumentError("{}: No username supplied".format(self))
                    
        self.client = self.create(self.service_type, username=self.username, password=self.password,
                                  host_info=self.host_info, auto_login=False)
        self.client.register()        