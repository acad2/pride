import pride.importers
import inspect
d = pride.importers.Dereference_Macro()
source = \
"""def test(self):
    ->"Python".do_stuff()"""
_source = d.handle_source(source)
print _source
code = compile(_source, 'test', 'exec')

#->self.source_name.add_listener(self.instance_name)
#self.instance_name->"Python"->'Network'
#test_get_instance_ref()->"Some_Object"->func(argument)->instance_name
#instance = test_get_ref()->"Some_Object"
#->self.instance_name->"Python"->'Network'

#->self.instance_name#, "Python", "Network")