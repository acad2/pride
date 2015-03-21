"""Restores an environment suspended by metapython.Metapython.save_state"""
if __name__ == "__main__":
    from mpre.metapython import *
    interpreter = Restored_Interpreter(parse_args=True)
    interpreter.start_machine()