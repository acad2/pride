from base import Instruction
Instruction("Machine", "create", "sdllibrary.SDL_Window").execute()
Instruction("System", "create", "metapython.Shell").execute()
Instruction("SDL_Window", "create", "guilibrary.Organizer").execute()
"""Instruction("SDL_Window", "draw", "text", 0, "This is a test :)", (200, 200, 200, 16)).execute()
Instruction("SDL_Window", "draw", "rect", 0, (200, 200, 200, 16), color=(255, 255, 255)).execute()
Instruction("SDL_Window", "draw", "line", 0, (0, 15, 15, 300, 60, 80, 100, 120), color=(55, 200, 130)).execute()
Instruction("SDL_Window", "draw", "point", 0, (300, 300, 300, 350, 300, 400, 300, 450), color=(255, 255, 255)).execute()"""
Instruction("SDL_Window", "create", "widgetlibrary.Homescreen").execute()
