import contextlib
import sys

import mpre.shell
import mpre.errors
import mpre.utilities
        
class Registration(mpre.shell.Program):
    
    defaults = mpre.shell.Program.defaults.copy()
    defaults.update({"name" : "registration",
                     "ip" : "localhost",
                     "port" : 40022})
    
    parser_ignore = mpre.shell.Program.parser_ignore + ("name", "client_name")

    def handle_input(self, input):
        with mpre.utilities.sys_argv_swapped([sys.argv[0]] + input.split()):
            client = self.create(mpre.shell.get_user_input("Please enter the authentication client name in the form package.module...class: "),
                                 parse_args=True, auto_login=False)        
        client.register()           
        
        
if __name__ == "__main__":
    registration = Registration(parse_args=True)
    registration.handle_input(mpre.shell.get_user_input("specify options, if any: "))