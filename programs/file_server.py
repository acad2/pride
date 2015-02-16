import mpre.base as base

def metapython_main():
    base.Instruction("System", "create", "network2.File_Service", parse_args=True).execute()

if __name__ == "__main__":
    metapython_main()
