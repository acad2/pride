#   mpf.send_file - sends a file via udp to the specified address

import mpre.base as base
Instruction = base.Instruction

def metapython_main():
    Instruction("Metapython", "create", "network2.File_Service", exit_when_finished=True).execute()
    Instruction("File_Service", "send_file", parse_args=True).execute()
    
if __name__ == "__main__":
    metapython_main()