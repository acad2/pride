mpre.gui.sdllibrary
========
No documentation available

Display_Wrapper
--------
	used by the display internally to display all objects

Default values for newly created instances:

- layer                    1
- popup                    False
- deleted                  False
- outline_width            5
- pack_modifier            
- held                     False
- pack_mode                
- memory_size              4096
- pack_on_init             True
- size                     [800, 600]
- network_packet_size      4096
- color_scalar             0.6
- verbosity                
- color                    (45, 150, 245)
- y                        0
- x                        0

This object defines the following non-private methods:


- **click**(self):

		  No documentation available



- **press**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.gui.sdllibrary.Display_Wrapper', class 'mpre.base.Wrapper', class 'mpre.base.Base', type 'object')


Font_Manager
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- default_font_size        14
- deleted                  False
- verbosity                
- default_color            (15, 180, 35)
- default_background       (0, 0, 0)
- memory_size              4096
- font_path                ./resources/fonts/Aero.ttf

No non-private methods are defined

This objects method resolution order is:

(class 'mpre.gui.sdllibrary.Font_Manager', class 'mpre.gui.sdllibrary.SDL_Component', class 'mpre.base.Wrapper', class 'mpre.base.Base', type 'object')


Instruction
--------
No documentation available

Renderer
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- deleted                  False
- verbosity                
- memory_size              4096
- componenttypes           ()

This object defines the following non-private methods:


- **draw_rect_width**(self, area, **kwargs):

		  No documentation available



- **draw_text**(self, text, rect, **kwargs):

		  No documentation available


This objects method resolution order is:

(class 'mpre.gui.sdllibrary.Renderer', class 'mpre.gui.sdllibrary.SDL_Component', class 'mpre.base.Wrapper', class 'mpre.base.Base', type 'object')


SDL_Component
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- deleted                  False
- verbosity                
- memory_size              4096

No non-private methods are defined

This objects method resolution order is:

(class 'mpre.gui.sdllibrary.SDL_Component', class 'mpre.base.Wrapper', class 'mpre.base.Base', type 'object')


SDL_Window
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- layer                    0
- name                     Metapython
- deleted                  False
- verbosity                
- color                    (0, 0, 0)
- memory_size              4096
- y                        0
- x                        0
- showing                  True
- size                     [800, 600]

This object defines the following non-private methods:


- **draw**(self, item, mode, area, z, *args, **kwargs):

		  No documentation available



- **run**(self):

		  No documentation available



- **get_mouse_state**(self):

		  No documentation available



- **create**(self, *args, **kwargs):

		  No documentation available



- **get_mouse_position**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.gui.sdllibrary.SDL_Window', class 'mpre.gui.sdllibrary.SDL_Component', class 'mpre.base.Wrapper', class 'mpre.base.Base', type 'object')


Sprite_Factory
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- deleted                  False
- verbosity                
- memory_size              4096

No non-private methods are defined

This objects method resolution order is:

(class 'mpre.gui.sdllibrary.Sprite_Factory', class 'mpre.gui.sdllibrary.SDL_Component', class 'mpre.base.Wrapper', class 'mpre.base.Base', type 'object')


User_Input
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- keyboard_input           
- deleted                  False
- verbosity                
- priority                 0.04
- memory_size              4096
- network_buffer           
- auto_start               True

This object defines the following non-private methods:


- **run**(self):

		  No documentation available



- **handle_mousebuttonup**(self, instruction):

		  No documentation available



- **handle_mousemotion**(self, instruction):

		  No documentation available



- **handle_quit**(self, instruction):

		  No documentation available



- **handle_mousebuttondown**(self, instruction):

		  No documentation available



- **handle_mousewheel**(self, instruction):

		  No documentation available



- **handle_keydown**(self, instruction):

		  No documentation available



- **mouse_is_inside**(self, area, mouse_pos_x, mouse_pos_y):

		  No documentation available



- **handle_unhandled_instruction**(self, instruction):

		  No documentation available



- **add_popup**(self, item):

		  No documentation available



- **handle_keyup**(self, instruction):

		  No documentation available



- **get_hotkey**(self, instance, key_press):

		  No documentation available


This objects method resolution order is:

(class 'mpre.gui.sdllibrary.User_Input', class 'mpre.vmlibrary.Process', class 'mpre.base.Base', type 'object')


itemgetter
--------
itemgetter(item, ...) --> itemgetter object

Return a callable object that fetches the given item(s) from its operand.
After f = itemgetter(2), the call f(r) returns r[2].
After g = itemgetter(2, 5, 3), the call g(r) returns (r[2], r[5], r[3])