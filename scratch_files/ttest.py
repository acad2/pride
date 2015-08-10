from mpre.misc.decoratorlibrary import Timed

connecting = set([x for x in xrange(500)][::2])
writable = [x for x in list(connecting)[::2]]
still_connecting = connecting.difference(writable)

def test_intersection():
    for accepted in connecting.intersection(writable):
        accepted
    new_connecting = connecting.difference(writable)
    
def test_generator():
    for accepted in (sock for sock in connecting if sock in writable):
        accepted
    new_connecting = set((sock for sock in connecting if sock not in writable))
    
def test_set_iter():
    for item in connecting:
        item
        
def test_list_iter():
    for item in list(connecting):
        item
        
def test_add():    
    new_set = set()
    for item in still_connecting:
        new_set.add(item)
        
def test_update_genexp():
    new_set = set()
    new_set.update((item for item in still_connecting if not False))
            
import base
b = base.Base(empty_list=[])
def test_build_list():
    for x in xrange(10000):
        r, w, e = [], [], []
        
def test_reuse_list():
    global b
    _b = b
    for x in xrange(10000):
        r, w, e = [], [], _b.empty_list
        
print Timed(test_build_list, 100)()
print Timed(test_reuse_list, 100)()        