import contextlib
import sys

import pride
import pride.shell
import pride.errors
import pride.utilities
        
class Registration(pride.shell.Program):
    
    defaults = pride.shell.Program.defaults.copy()
    defaults.update({"name" : "registration",
                     "ip" : "localhost",
                     "port" : 40022})
    
    parser_ignore = pride.shell.Program.parser_ignore + ("name", "client_name")

    def handle_input(self, input):
        with pride.utilities.sys_argv_swapped([sys.argv[0]] + input.split()):
            client = pride.objects["->Python"].create(pride.shell.get_user_input("Please enter the authentication client name in the form package.module...class: "),
                                                      parse_args=True, auto_login=False,
                                                      _register_results=sys.exit)        
        client.register()           
        
        
if __name__ == "__main__":
    registration = Registration(parse_args=True)
    registration.handle_input(pride.shell.get_user_input("specify options, if any: "))