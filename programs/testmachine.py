import machinelibrary

test_machine = machinelibrary.Machine()
test_machine.create("interpreter.Shell")

if __name__ == "__main__":
    test_machine.run()