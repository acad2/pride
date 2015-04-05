mpre.gui.widgetlibrary
========
No documentation available

Attribute_Displayer
--------
	No docstring found

Default values for newly created instances:

- layer                    1
- popup                    False
- show_title_bar           False
- memory_mode              -1
- deleted                  False
- outline_width            5
- pack_modifier            
- held                     False
- pack_mode                layer
- memory_size              4096
- background_color         (0, 0, 0)
- pack_on_init             True
- size                     [800, 600]
- color_scalar             0.6
- color                    (0, 115, 10)
- verbosity                
- sdl_window               SDL_Window
- update_flag              False
- y                        0
- x                        0

No non-private methods are defined

This objects method resolution order is:

(class 'mpre.gui.widgetlibrary.Attribute_Displayer', class 'mpre.gui.guilibrary.Window', class 'mpre.gui.guilibrary.Window_Object', class 'mpre.base.Base', type 'object')


Date_Time_Button
--------
	No docstring found

Default values for newly created instances:

- layer                    1
- popup                    False
- show_title_bar           False
- memory_mode              -1
- deleted                  False
- text                     Button
- outline_width            5
- text_color               (255, 130, 25)
- pack_modifier            
- held                     False
- pack_mode                horizontal
- memory_size              4096
- alpha                    1
- background_color         (0, 0, 0)
- pack_on_init             True
- size                     [800, 600]
- color_scalar             0.6
- verbosity                
- sdl_window               SDL_Window
- shape                    rect
- color                    (0, 115, 10)
- update_flag              False
- y                        0
- x                        0

This object defines the following non-private methods:


- **update_time**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.gui.widgetlibrary.Date_Time_Button', class 'mpre.gui.guilibrary.Button', class 'mpre.gui.guilibrary.Window_Object', class 'mpre.base.Base', type 'object')


Homescreen
--------
	No docstring found

Default values for newly created instances:

- layer                    1
- popup                    False
- show_title_bar           False
- memory_mode              -1
- deleted                  False
- outline_width            5
- pack_modifier            
- held                     False
- pack_mode                layer
- memory_size              4096
- background_color         (0, 0, 0)
- pack_on_init             True
- size                     [800, 600]
- color_scalar             0.6
- verbosity                
- sdl_window               SDL_Window
- color                    (0, 115, 10)
- update_flag              False
- y                        0
- x                        0
- background_filename      C:\test.jpg

No non-private methods are defined

This objects method resolution order is:

(class 'mpre.gui.widgetlibrary.Homescreen', class 'mpre.gui.guilibrary.Window', class 'mpre.gui.guilibrary.Window_Object', class 'mpre.base.Base', type 'object')


Indicator
--------
	No docstring found

Default values for newly created instances:

- layer                    1
- popup                    False
- show_title_bar           False
- memory_mode              -1
- deleted                  False
- text                     Button
- outline_width            5
- text_color               (255, 130, 25)
- pack_modifier            
- held                     False
- pack_mode                vertical
- memory_size              4096
- alpha                    1
- background_color         (0, 0, 0)
- pack_on_init             True
- size                     [800, 600]
- color_scalar             0.6
- color                    (0, 115, 10)
- verbosity                
- shape                    rect
- sdl_window               SDL_Window
- update_flag              False
- y                        0
- x                        0

This object defines the following non-private methods:


- **draw_texture**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.gui.widgetlibrary.Indicator', class 'mpre.gui.guilibrary.Button', class 'mpre.gui.guilibrary.Window_Object', class 'mpre.base.Base', type 'object')


Instruction
--------
 usage: Instruction(component_name, method_name, 
                           *args, **kwargs).execute(priority=priority)
                           
        Creates and executes an instruction object. 
            - component_name is the string instance_name of the component 
            - method_name is a string of the component method to be called
            - Positional and keyword arguments for the method may be
              supplied after the method_name.
              
        A priority attribute can be supplied when executing an instruction.
        It defaults to 0.0 and is the time in seconds until this instruction
        will actually be performed.
        
        Instructions are useful for serial and explicitly timed tasks. 
        Instructions are only enqueued when the execute method is called. 
        At that point they will be marked for execution in 
        instruction.priority seconds. 
        
        Instructions may be saved as an attribute of a component instead
        of continuously being instantiated. This allows the reuse of
        instruction objects. The same instruction object can be executed 
        any number of times.
        
        Note that Instructions must be executed to have any effect, and
        that they do not happen inline, even if priority is 0.0. 
        Because they do not execute in the current scope, the return value 
        from the method call is not available through this mechanism.

Popup_Menu
--------
	No docstring found

Default values for newly created instances:

- layer                    1
- popup                    True
- show_title_bar           False
- memory_mode              -1
- deleted                  False
- outline_width            5
- pack_modifier            <function <lambda> at 0x024B8A30>
- held                     False
- pack_mode                vertical
- memory_size              4096
- alpha                    1
- background_color         (0, 0, 0)
- pack_on_init             True
- size                     [800, 600]
- color_scalar             0.6
- color                    (0, 115, 10)
- verbosity                
- sdl_window               SDL_Window
- update_flag              False
- y                        0
- x                        0

No non-private methods are defined

This objects method resolution order is:

(class 'mpre.gui.widgetlibrary.Popup_Menu', class 'mpre.gui.guilibrary.Container', class 'mpre.gui.guilibrary.Window_Object', class 'mpre.base.Base', type 'object')


Right_Click_Button
--------
	No docstring found

Default values for newly created instances:

- layer                    1
- popup                    False
- show_title_bar           False
- memory_mode              -1
- deleted                  False
- text                     Button
- outline_width            5
- text_color               (255, 130, 25)
- pack_modifier            
- held                     False
- pack_mode                vertical
- memory_size              4096
- alpha                    1
- background_color         (0, 0, 0)
- pack_on_init             True
- size                     [800, 600]
- color_scalar             0.6
- verbosity                
- sdl_window               SDL_Window
- shape                    rect
- color                    (0, 115, 10)
- update_flag              False
- y                        0
- x                        0

This object defines the following non-private methods:


- **click**(self, mouse):

		  No documentation available


This objects method resolution order is:

(class 'mpre.gui.widgetlibrary.Right_Click_Button', class 'mpre.gui.guilibrary.Button', class 'mpre.gui.guilibrary.Window_Object', class 'mpre.base.Base', type 'object')


Right_Click_Menu
--------
	No docstring found

Default values for newly created instances:

- layer                    1
- popup                    True
- show_title_bar           False
- memory_mode              -1
- deleted                  False
- outline_width            5
- pack_modifier            <function <lambda> at 0x024B8A30>
- held                     False
- pack_mode                layer
- memory_size              4096
- alpha                    1
- background_color         (0, 0, 0)
- pack_on_init             True
- size                     (200, 150)
- color_scalar             0.6
- verbosity                
- sdl_window               SDL_Window
- color                    (0, 115, 10)
- update_flag              False
- y                        0
- x                        0

No non-private methods are defined

This objects method resolution order is:

(class 'mpre.gui.widgetlibrary.Right_Click_Menu', class 'mpre.gui.widgetlibrary.Popup_Menu', class 'mpre.gui.guilibrary.Container', class 'mpre.gui.guilibrary.Window_Object', class 'mpre.base.Base', type 'object')


Task_Bar
--------
	No docstring found

Default values for newly created instances:

- layer                    1
- popup                    False
- show_title_bar           False
- memory_mode              -1
- deleted                  False
- outline_width            5
- pack_modifier            <function <lambda> at 0x024B8A70>
- held                     False
- pack_mode                menu_bar
- memory_size              4096
- alpha                    1
- background_color         (0, 0, 0)
- pack_on_init             True
- size                     [800, 600]
- color_scalar             0.6
- verbosity                
- sdl_window               SDL_Window
- color                    (0, 115, 10)
- update_flag              False
- y                        0
- x                        0

No non-private methods are defined

This objects method resolution order is:

(class 'mpre.gui.widgetlibrary.Task_Bar', class 'mpre.gui.guilibrary.Container', class 'mpre.gui.guilibrary.Window_Object', class 'mpre.base.Base', type 'object')


Title_Bar
--------
	No docstring found

Default values for newly created instances:

- layer                    1
- popup                    False
- show_title_bar           False
- memory_mode              -1
- deleted                  False
- outline_width            5
- pack_modifier            
- held                     False
- pack_mode                vertical
- memory_size              4096
- alpha                    1
- background_color         (0, 0, 0)
- pack_on_init             True
- size                     [800, 600]
- color_scalar             0.6
- verbosity                
- sdl_window               SDL_Window
- color                    (0, 115, 10)
- update_flag              False
- y                        0
- x                        0

This object defines the following non-private methods:


- **draw_texture**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.gui.widgetlibrary.Title_Bar', class 'mpre.gui.guilibrary.Container', class 'mpre.gui.guilibrary.Window_Object', class 'mpre.base.Base', type 'object')
