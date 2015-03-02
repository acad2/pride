import os
import mpre.defaults as defaults
Base = defaults.Base
Process = defaults.Process

PACKAGE_LOCATION = os.path.dirname(os.path.abspath(__file__))

SCREEN_SIZE = [800, 600]
#R = 45
#G = 150
#B = 245
R = 0
G = 115
B = 10
# sdllibrary

SDL_Component = Base.copy()

World = SDL_Component.copy()
World.update({"displays" : ({"display_number" : 0}, )})

SDL_Window = SDL_Component.copy()
SDL_Window.update({"size" : SCREEN_SIZE,
"showing" : True,
"layer" : 0,
"name" : "Metapython",
"color" : (0, 0, 0),
"x" : 0,
"y" : 0})

Renderer = SDL_Component.copy()
Renderer.update({"componenttypes" : tuple()})

User_Input = Process.copy()
#User_Input.update({"priority" : .01})

Sprite_Factory = SDL_Component.copy()

Font_Manager = SDL_Component.copy()
Font_Manager.update({"font_path" : os.path.join(PACKAGE_LOCATION, "resources",
                                                "fonts", "Aero.ttf"),
"default_font_size" : 14,
"default_color" : (15, 180, 35),
"default_background" : (0, 0, 0)})

# guilibrary

Organizer = Process.copy()
Organizer.update({"priority" : 0})

Window_Object = Base.copy()
Window_Object.update({'x' : 0,
'y' : 0,
'size' : SCREEN_SIZE,
"layer" : 1,
"background_color" : (0, 0, 0),
"color" : (R, G, B),
"outline_width" : 5,
"popup" : False,
"pack_mode" : '',
"held" : False,
"pack_modifier" : '',
"color_scalar" : .6,
"pack_on_init" : True})

Window = Window_Object.copy()
Window.update({"show_title_bar" : False,
"pack_mode" : "layer"})

Container = Window.copy()
Container.update({"alpha" : 1,
"pack_mode" : "vertical"})

Button = Container.copy()
Button.update({"shape" : "rect",
"text" : "Button",
"text_color" : (255, 130, 25)})


# widgetlibrary
Popup_Menu = Container.copy()
Popup_Menu.update({"popup" : True,
"pack_modifier" : lambda parent, child: setattr(child, "position", (SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/2))})

File_Menu = Popup_Menu.copy()
File_Menu.update({"pack_mode" : "vertical",
        "pack_modifier" : lambda parent, child: setattr(child, "y", child.y+parent.size[1])})

Right_Click_Menu = Popup_Menu.copy()
Right_Click_Menu.update({"pack_mode": "layer",
"size" : (200, 150)})

Right_Click_Button = Button.copy()

Homescreen = Window.copy()
Homescreen.update({"background_filename" : "C:\\test.jpg"})

Property_Editor = Window.copy()
Property_Editor.update({"pack_modifier" : lambda parent, child:\
setattr(child, "position", (SCREEN_SIZE[0]/2, SCREEN_SIZE[1]/2))})

Menu_Bar = Container.copy()
Menu_Bar.update({"pack_mode" : "menu_bar"})

Title_Bar = Menu_Bar.copy()
Title_Bar.update({"pack_modifier" : lambda parent, child:\
setattr(child, "y", child.y+child.size[1])})

Task_Bar = Menu_Bar.copy()
Task_Bar.update({"pack_modifier" : lambda parent, child:\
setattr(child, "y", (parent.y+parent.size[1])-child.size[1])\
}) # ^ aligns the bottom left corners of the parent and child object

Date_Time_Button = Button.copy()
Date_Time_Button.update({"pack_mode" : "horizontal"})

Help_Bar = Button.copy()
Help_Bar.update({"pack_mode" : "horizontal"})

Property_Button = Button.copy()
Property_Button.update({"property" : '',
"display" : False})

File_Button = Button.copy()
File_Button.update({"display" : False})

Text_Line = Button.copy()
Text_Line.update({"edit_mode" : False})

Text_Character = Button.copy()
Text_Character.update({"text" : "",
        "pack_mode" : "text",
        "outline" : 0})
