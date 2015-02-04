mpre.gui.guilibrary
========
No documentation available

Button
--------
	No docstring found

Default values for newly created instances:

- layer                    1
- popup                    False
- show_title_bar           False
- deleted                  False
- text                     Button
- outline_width            5
- text_color               (255, 130, 25)
- pack_modifier            
- held                     False
- pack_mode                vertical
- memory_size              4096
- alpha                    1
- pack_on_init             True
- size                     [800, 600]
- network_packet_size      4096
- color_scalar             0.6
- verbosity                
- shape                    rect
- color                    (45, 150, 245)
- y                        0
- x                        0

This object defines the following non-private methods:


- **draw_texture**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.gui.guilibrary.Button', class 'mpre.gui.guilibrary.Window_Object', class 'mpre.base.Base', type 'object')


Container
--------
	No docstring found

Default values for newly created instances:

- layer                    1
- popup                    False
- show_title_bar           False
- deleted                  False
- outline_width            5
- pack_modifier            
- held                     False
- pack_mode                vertical
- memory_size              4096
- alpha                    1
- pack_on_init             True
- size                     [800, 600]
- network_packet_size      4096
- color_scalar             0.6
- verbosity                
- color                    (45, 150, 245)
- y                        0
- x                        0

No non-private methods are defined

This objects method resolution order is:

(class 'mpre.gui.guilibrary.Container', class 'mpre.gui.guilibrary.Window_Object', class 'mpre.base.Base', type 'object')


Instruction
--------
No documentation available

Organizer
--------
	No docstring found

Default values for newly created instances:

- network_packet_size      4096
- keyboard_input           
- deleted                  False
- verbosity                
- priority                 0
- memory_size              4096
- network_buffer           
- auto_start               True

This object defines the following non-private methods:


- **run**(self):

		  No documentation available



- **pack_menu_bar**(self, item, count, length):

		  No documentation available



- **pack_vertical**(self, item, count, length):

		  No documentation available



- **pack_text**(self, item, count, length):

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

(class 'mpre.gui.guilibrary.Organizer', class 'mpre.vmlibrary.Process', class 'mpre.base.Base', type 'object')


SDL_Rect
--------
No documentation available

Window
--------
	No docstring found

Default values for newly created instances:

- layer                    1
- popup                    False
- show_title_bar           False
- deleted                  False
- outline_width            5
- pack_modifier            
- held                     False
- pack_mode                layer
- memory_size              4096
- pack_on_init             True
- size                     [800, 600]
- network_packet_size      4096
- color_scalar             0.6
- verbosity                
- color                    (45, 150, 245)
- y                        0
- x                        0

No non-private methods are defined

This objects method resolution order is:

(class 'mpre.gui.guilibrary.Window', class 'mpre.gui.guilibrary.Window_Object', class 'mpre.base.Base', type 'object')


Window_Object
--------
	No docstring found

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


- **mousewheel**(self, x_amount, y_amount):

		  No documentation available



- **draw**(self, figure='rect', *args, **kwargs):

		  No documentation available



- **press**(self, mouse):

		  No documentation available



- **click**(self, mouse):

		  No documentation available



- **mousemotion**(self, x_change, y_change):

		  No documentation available



- **create**(self, *args, **kwargs):

		  No documentation available



- **release**(self, mouse):

		  No documentation available



- **pack**(self, reset=False):

		  No documentation available



- **draw_texture**(self):

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