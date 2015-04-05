mpre.game.character
========
No documentation available

Character
--------
	No docstring found

Default values for newly created instances:

- dodge                    0
- layer                    1
- popup                    False
- show_title_bar           False
- avoid_effects            ('Damage', 'Curse', 'Interrupt')
- memory_mode              -1
- deleted                  False
- text                     Button
- outline_width            5
- text_color               (255, 130, 25)
- pack_modifier            
- held                     False
- pack_mode                vertical
- memory_size              4096
- draw_indicator           True
- x                        0
- alpha                    1
- background_color         (0, 0, 0)
- pack_on_init             True
- size                     (50, 100)
- color_scalar             0.6
- color                    (0, 115, 10)
- name                     
- equipment                {'head': None, 'wrists': None, 'back': None, 'arms': None, 'feet': None, 'hands': None, 'waist': None, 'neck': None, 'shoulders': None, 'fingers': None, 'face': None, 'chest': None, 'thighs': None, 'legs': None}
- verbosity                
- level                    1
- damage                   0
- experience               0
- shape                    rect
- sdl_window               SDL_Window
- update_flag              False
- y                        0
- position                 (0, 0)

This object defines the following non-private methods:


- **die**(self):

		  No documentation available



- **drop**(self, item):

		  No documentation available



- **define_spell**(self, spell_name, *args):

		  No documentation available



- **cast**(self, spell_name, target=None, **kwargs):

		  No documentation available



- **draw_texture**(self):

		  No documentation available


This objects method resolution order is:

(class 'mpre.game.character.Character', class 'mpre.game.gamelibrary.Game_Object', class 'mpre.gui.guilibrary.Button', class 'mpre.gui.guilibrary.Window_Object', class 'mpre.base.Base', type 'object')


Npc
--------
	No docstring found

Default values for newly created instances:

- layer                    1
- color                    (0, 115, 10)
- text                     Button
- color_scalar             0.6
- held                     False
- draw_indicator           True
- memory_size              4096
- background_color         (0, 0, 0)
- pack_on_init             True
- size                     (50, 100)
- damage                   0
- equipment                {'head': None, 'wrists': None, 'back': None, 'arms': None, 'feet': None, 'hands': None, 'waist': None, 'neck': None, 'shoulders': None, 'fingers': None, 'face': None, 'chest': None, 'thighs': None, 'legs': None}
- dodge                    0
- outline_width            5
- popup                    False
- show_title_bar           False
- avoid_effects            ('Damage', 'Curse', 'Interrupt')
- memory_mode              -1
- deleted                  False
- text_color               (255, 130, 25)
- pack_modifier            
- pack_mode                vertical
- position                 (0, 0)
- alpha                    1
- name                     
- level                    1
- verbosity                
- sdl_window               SDL_Window
- shape                    rect
- experience               0
- update_flag              False
- y                        0
- x                        0

No non-private methods are defined

This objects method resolution order is:

(class 'mpre.game.character.Npc', class 'mpre.game.character.Character', class 'mpre.game.gamelibrary.Game_Object', class 'mpre.gui.guilibrary.Button', class 'mpre.gui.guilibrary.Window_Object', class 'mpre.base.Base', type 'object')


Player
--------
	No docstring found

Default values for newly created instances:

- layer                    1
- color                    (0, 115, 10)
- text                     Button
- color_scalar             0.6
- held                     False
- draw_indicator           True
- memory_size              4096
- background_color         (0, 0, 0)
- pack_on_init             True
- size                     (50, 100)
- damage                   0
- equipment                {'head': None, 'wrists': None, 'back': None, 'arms': None, 'feet': None, 'hands': None, 'waist': None, 'neck': None, 'shoulders': None, 'fingers': None, 'face': None, 'chest': None, 'thighs': None, 'legs': None}
- dodge                    0
- outline_width            5
- popup                    False
- show_title_bar           False
- avoid_effects            ('Damage', 'Curse', 'Interrupt')
- memory_mode              -1
- deleted                  False
- text_color               (255, 130, 25)
- pack_modifier            
- pack_mode                vertical
- position                 (0, 0)
- alpha                    1
- name                     
- level                    1
- verbosity                
- sdl_window               SDL_Window
- shape                    rect
- experience               0
- update_flag              False
- y                        0
- x                        0

No non-private methods are defined

This objects method resolution order is:

(class 'mpre.game.character.Player', class 'mpre.game.character.Character', class 'mpre.game.gamelibrary.Game_Object', class 'mpre.gui.guilibrary.Button', class 'mpre.gui.guilibrary.Window_Object', class 'mpre.base.Base', type 'object')
