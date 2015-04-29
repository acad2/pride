"""Restores an environment suspended by metapython.Metapython.save_state"""
if __name__ == "__main__":
    import mpre._metapython
    interpreter = mpre._metapython.Restored_Interpreter(parse_args=True)
    interpreter.start_machine()