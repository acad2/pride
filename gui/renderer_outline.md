A quick explanation of a scalable, lazy renderer:

A "layer" consists of all the textures that have the same z attribute.
Layers are marked as invalid whenever a texture in that layer is modified. 
Layers are managed when the renderer runs, which is at a set framerate. 
The max layer and the highest invalid layer are kept track of. The renderer 
starts at the highest invalid layer and ends at the max layer. Each layer is
set as the renderer target and cleared. The previous layer is then copied to
the current layer. Then it iterates through each texture in the layer, 
redrawing those marked invalid, and copies each texture on top of the current 
layer. The result is that the previous layer is the background while the 
current layer drawn on top of it. This texture is cached and invalidated when 
the layer is marked invalid. After running through any invalid layers, set the
render target back to default (null), copy the highest texture to the screen, 
and present.

In a 2d with layers user interface type of environment, the above is 
scalable and lazy. On my low end Celeron n2830 my test applications idle at
0% cpu usage. It more or less stayed that way even when I added a hundred
test layers. Since it only draws from what layer changed upwards, and all
changes are enqueued at a reasonable framerate, very little work actually
ends up being done. Iterating through the invalid layer to the max layer appears
asymptotically friendlier then iterating through all layers every run. Running
the renderer at a set interval and doing all the drawing then helps to save time
because it will ignore excess changes that wouldn't have been seen anyways. 
It's been worth it to use some application code to avoid having to draw
stuff and copy textures. Those tend to take longer then a few if checks and 
attribute lookups. 

note that this design was intended for 2d with layers, like a user interface.
some principles may not neccessarily work well in other environments.

Also the above only supports textures and not surfaces. Mixing the two
was for me not worth the complexity. Getting the sdl2 renderer to draw to a 
particular texture took some figuring out, but serves my needs well enough 
alone. If you mix the two it appears difficult to avoid some additional work.
Plus textures benefit from a gpu, which adds to efficiency wins in terms of 
cpu time.

In my system, window objects have a draw method. This method enqueues draw
operations with the renderer instead of drawing them immediately. Window
objects have an area attribute. To support objects that do not have an area 
attribute, maybe you could apply a wrapper that does around your object that 
does not. That way when prompted for an area it can still provide one, even 
though it doesn't have one internally. Or maybe use a table that maps
your object to an area, or a method call of whatever object does track its
texture.

Note that this draw method is a hybrid approach of objects drawing themselves and
the renderer drawing objects. The objects appear to draw themselves, while the
renderer actually does the work. 

In short:    
    textures are signficantly faster then surfaces
    enqueue draw and copy operations for batch processing
    cache textures when they are drawn
    cache layers after copying all textures to them    
    use the caches to avoid rendering all but the invalid layers to max layer
    