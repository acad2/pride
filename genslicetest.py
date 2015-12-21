class Sliceable_Generator(object):
    
    def __init__(self, generator):
        self.generator = generator
        for attribute in (name for name in dir(generator) if "__" != name[:2]):
            setattr(self, attribute, getattr(generator, attribute))
            
    def __getitem__(self, slice):
        start = slice.start if slice.start is not None else 0   
        stop = slice.stop if slice.stop is not None else 0
        if stop < start:
            raise IndexError("Unable to slice generator in reverse")
            
        generator = self.generator
        if start:
            for count in range(start):
                next(generator)
        
        step = slice.step if slice.step is not None else 1
        ignore_slices = range(step - 1)
        item_count = stop - start
        for counter in range(item_count) if item_count else itertools.count():                
            yield next(generator)
            for ignore_slice in ignore_slices:
                next(generator)            
        
if __name__ == "__main__":
    generator = Sliceable_Generator((x for x in range(128)))
    for number in generator[11:127:2]:
        print number