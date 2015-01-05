from base import Event
Event("Machine", "create", "sdllibrary.SDL_Window").post()
Event("System", "create", "metapython.Shell").post()
Event("SDL_Window", "create", "guilibrary.Organizer").post()
"""Event("SDL_Window", "draw", "text", 0, "This is a test :)", (200, 200, 200, 16)).post()
Event("SDL_Window", "draw", "rect", 0, (200, 200, 200, 16), color=(255, 255, 255)).post()
Event("SDL_Window", "draw", "line", 0, (0, 15, 15, 300, 60, 80, 100, 120), color=(55, 200, 130)).post()
Event("SDL_Window", "draw", "point", 0, (300, 300, 300, 350, 300, 400, 300, 450), color=(255, 255, 255)).post()"""
Event("SDL_Window", "create", "widgetlibrary.Homescreen").post()