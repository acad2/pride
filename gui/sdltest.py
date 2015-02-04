import mpre.base as base 
Instruction = base.Instruction

if __name__ == "__main__":
    Instruction("Machine", "create", "sdllibrary.SDL_Window").execute()
    Instruction("System", "create", "metapython.Shell").execute()
    Instruction("SDL_Window", "create", "guilibrary.Organizer").execute()
    Instruction("SDL_Window", "create", "widgetlibrary.Homescreen").execute()