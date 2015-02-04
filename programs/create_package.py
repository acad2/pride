import mpre.package

    
if __name__ == "__main__":
    Instruction("Metapython", "exit").execute()
    package = mpre.package.Package(parse_args=True)
    