import mpre
Instruction = mpre.Instruction

if __name__ == "__main__":
    Instruction("Metapython", "create", "network2.File_Service", exit_when_finished=True).execute()
    Instruction("File_Service", "send_file", parse_args=True).execute()