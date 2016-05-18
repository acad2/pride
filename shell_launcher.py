# pride.shell_launcher - default module for launching the python shell 
import pride.user

if __name__ == "__main__":     
    user = pride.user.User(parse_args=True)            
    user.create("pride.interpreter.Shell", username=user.username, parse_args=True)
    command_line = user.objects["Command_Line"][0]
    python_shell = command_line.create("pride.shell.Python_Shell")
    command_line.set_default_program(python_shell.name, (python_shell.reference, "handle_input"), set_backup=True)