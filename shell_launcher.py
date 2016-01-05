# pride.shell_launcher - configuration file for launching the shell 
import pride.user

if __name__ == "__main__":     
    user = pride.user.User(parse_args=True)            
    user.create("pride.interpreter.Shell", username=user.username, parse_args=True)