mpre.gui.guilibrary
========
No documentation available

Button
--------
	No docstring found

Default values for newly created instances:

- layer                    : 1
- popup                    : False
- show_title_bar           : False
- memory_mode              : -1
- deleted                  : False
- text                     : Button
- outline_width            : 5
- text_color               : (255, 130, 25)
- pack_modifier            : 
- held                     : False
- pack_mode                : vertical
- memory_size              : 4096
- alpha                    : 1
- background_color         : (0, 0, 0)
- pack_on_init             : True
- size                     : [800, 600]
- color_scalar             : 0.6
- color                    : (0, 115, 10)
- verbosity                : 
- shape                    : rect
- sdl_window               : SDL_Window
- y                        : 0
- x                        : 0

This object defines the following non-private methods:


- **draw_texture**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.gui.guilibrary.Button', class 'mpre.gui.guilibrary.Window_Object', class 'mpre.base.Base', type 'object')


Container
--------
	No docstring found

Default values for newly created instances:

- layer                    : 1
- popup                    : False
- show_title_bar           : False
- memory_mode              : -1
- deleted                  : False
- outline_width            : 5
- pack_modifier            : 
- held                     : False
- pack_mode                : vertical
- memory_size              : 4096
- alpha                    : 1
- background_color         : (0, 0, 0)
- pack_on_init             : True
- size                     : [800, 600]
- color_scalar             : 0.6
- verbosity                : 
- sdl_window               : SDL_Window
- color                    : (0, 115, 10)
- y                        : 0
- x                        : 0

No non-private methods are defined

This objects method resolution order is:

(class 'mpre.gui.guilibrary.Container', class 'mpre.gui.guilibrary.Window_Object', class 'mpre.base.Base', type 'object')


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
        that they do not happen inline even if the priority is 0.0. In
        order to access the result of the executed function, a callback
        function can be provided.

Organizer
--------
	No docstring found

Default values for newly created instances:

- priority                 : 0
- memory_size              : 4096
- memory_mode              : -1
- auto_start               : True
- deleted                  : False
- verbosity                : 

This object defines the following non-private methods:


- **pack_menu_bar**(self, item, count, length):

		  No documentation available



- **pack_text**(self, item, count, length):

		  No documentation available



- **pack_vertical**(self, item, count, length):

		  No documentation available



- **pack_layer**(self, item, count, length):

		  No documentation available



- **pack_grid**(self, item, count, length):

		  No documentation available



- **pack_horizontal**(self, item, count, length):

		  No documentation available



- **pack**(self, item):

		  No documentation available


This objects method resolution order is:

(class 'mpre.gui.guilibrary.Organizer', class 'mpre.base.Base', type 'object')


SDL_Rect
--------
No documentation available

Theme
--------
	No docstring found

Default values for newly created instances:

- layer                    : 1
- popup                    : False
- memory_mode              : -1
- deleted                  : False
- outline_width            : 5
- pack_modifier            : 
- held                     : False
- pack_mode                : 
- memory_size              : 4096
- background_color         : (0, 0, 0)
- pack_on_init             : True
- size                     : [800, 600]
- color_scalar             : 0.6
- color                    : (0, 115, 10)
- verbosity                : 
- sdl_window               : SDL_Window
- y                        : 0
- x                        : 0

This object defines the following non-private methods:


- **draw_texture**(self, window_object):

		  No documentation available


This objects method resolution order is:

(class 'mpre.gui.guilibrary.Theme', class 'mpre.gui.guilibrary.Window_Object', class 'mpre.base.Base', type 'object')


Window
--------
	No docstring found

Default values for newly created instances:

- layer                    : 1
- popup                    : False
- show_title_bar           : False
- memory_mode              : -1
- deleted                  : False
- outline_width            : 5
- pack_modifier            : 
- held                     : False
- pack_mode                : layer
- memory_size              : 4096
- background_color         : (0, 0, 0)
- pack_on_init             : True
- size                     : [800, 600]
- color_scalar             : 0.6
- color                    : (0, 115, 10)
- verbosity                : 
- sdl_window               : SDL_Window
- y                        : 0
- x                        : 0

No non-private methods are defined

This objects method resolution order is:

(class 'mpre.gui.guilibrary.Window', class 'mpre.gui.guilibrary.Window_Object', class 'mpre.base.Base', type 'object')


Window_Object
--------
	No docstring found

Default values for newly created instances:

- layer                    : 1
- popup                    : False
- memory_mode              : -1
- deleted                  : False
- outline_width            : 5
- pack_modifier            : 
- held                     : False
- pack_mode                : 
- memory_size              : 4096
- background_color         : (0, 0, 0)
- pack_on_init             : True
- size                     : [800, 600]
- color_scalar             : 0.6
- verbosity                : 
- sdl_window               : SDL_Window
- color                    : (0, 115, 10)
- y                        : 0
- x                        : 0

This object defines the following non-private methods:


- **click**(self, mouse):

		  No documentation available



- **mousemotion**(self, x_change, y_change):

		  No documentation available



- **create**(self, *args, **kwargs):

		  No documentation available



- **draw_children**(self):

		  No documentation available



- **add**(self, instance):

		  No documentation available



- **draw_texture**(self):

		  No documentation available



- **draw**(self, figure='rect', *args, **kwargs):

		  No documentation available



- **mousewheel**(self, x_amount, y_amount):

		  No documentation available



- **press**(self, mouse):

		  No documentation available



- **release**(self, mouse):

		  No documentation available



- **pack**(self, reset=False):

		  No documentation available



- **delete**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.gui.guilibrary.Window_Object', class 'mpre.base.Base', type 'object')


attrgetter
--------
attrgetter(attr, ...) --> attrgetter object

Return a callable object that fetches the given attribute(s) from its operand.
After f = attrgetter('name'), the call f(r) returns r.name.
After g = attrgetter('name', 'date'), the call g(r) returns (r.name, r.date).
After h = attrgetter('name.first', 'name.last'), the call h(r) returns
(r.name.first, r.name.last).