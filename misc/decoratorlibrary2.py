regular_template =\
"""def __call__({0}):
    if monkey_patch or decorator or decorators:
        modifier = [mod for mod in (monkey_patch, decorator, decorators) if mod][0]
        call = self.handler_map[modifier](locals()[modifier])
    else:
        call = self.function
    return """
    
varargs_template =\
"""def __call__({0}):
    check_for = kwargs.pop
    modifiers = ("monkey_patch", "decorator", "decorators")
    for modifier in modifiers:
        found = check_for(modifier, None)
        if found:
            call = self.handler_map[modifier](found)
            break
    else:
        call = self.function
    return """        
    
call_template = "call({})"

"""self.handler_map = {"monkey_patch" : self._handle_monkey_patch,
                            "decorator" : self._handle_decorator,
                            "decorators" : self._handle_decorators}"""
                            
class Decorator(object):
        
    def __init__(self, function):

        
        if default_args:
            new_args = []
            for arg in default_args:
                if isinstance(arg, str):
                    new_arg = repr(arg)
                else:
                    new_arg = arg
                new_args.append(new_arg)
            default_args = new_args
            non_defaults = len(args) - len(default_args)
            len(default_args)
            header_args = header_args[:non_defaults] + ["{}={}".format(arg_name, default_args[index]) for index, arg_name in enumerate(header_args[non_defaults:])]
            
        if varargs:
            header_size += "{}, "
            header_args.append("*"+varargs)
            template = self.varargs_template        
        
        if keyword_args:
            header_size += "{}, "
            header_args.append("**" + keyword_args)
            call_size += "{}, "
            call_args.append("**" + keyword_args)
            
        else:
            header_size += "{}, " * 3
            header_args.extend(("monkey_patch=None", "decorator=None", "decorators=None"))        
            
        ending = header_size.rfind(", ")
        header_size = header_size[:ending]
        
        ending = call_size.rfind(", ")
        call_size = call_size[:ending]
        
        self.header_size = header_size
        self.header_args = header_args
     #   print header_size, header_args
      #  print "header: {}".format(header_size).format(*header_args)
       # print "call sig: {}".format(call_size).format(*call_args)
        template = template.format(header_size).format(*header_args)
        template = template.replace("self.function.im_self", "self", 1)
        
        call_template = self.call_template.format(call_size).format(*call_args)
        
        ready_template = self.template = template + call_template
        new_code = compile(ready_template, "compiled", 'exec')

        results = {}
        exec new_code in locals(), results
        self.__call__  = results.pop("__call__")
        
        #print self, "__call__ is ", self.__call__()
        print "created custom call signature for", function.func_name
        if function.func_name == "attribute_setter":
            print call_args, call_size
            print call_template
            print inspect.getargspec(self.__call__)
            print ready_template
     
    def __call__(self):
        raise NotImplementedError

    def _handle_context_manager(self, args, kwargs):
        module_name, context_manager_name = self._resolve_string(kwargs.pop("context_manager"))
        module = self._get_module(module_name)
        context_manager = getattr(module, context_manager_name)
        with context_manager():
            result = self.function(*args, **kwargs)
        return result

    def _handle_monkey_patch(self, patch_info):
        module_name, patch_name = self._resolve_string(patch_info)
        module = self._get_module(module_name)
        monkey_patch = getattr(module, patch_name)
        try:
            result = functools.partial(monkey_patch, self.function.im_self)
        except AttributeError: # function has no attribute im_self (not a method)
            result = monkey_patch
        return result

    def _handle_decorator(self, decorator_type):
        module_name, decorator_name = self._resolve_string(decorator_type)
        decorator = self._get_decorator(decorator_name, module_name)
        return decorator(self.function)

    def _handle_decorators(self, decorator_names):
        decorators = []
        for item in decorator_names:
            module_name, decorator_name = self._resolve_string(item)
            decorator = self._get_decorator(decorator_name, module_name)
            decorators.append(decorator)

        wrapped_function = self.function
        for item in reversed(decorators):
            wrapped_function = item(wrapped_function)
        return wrapped_function

    def _resolve_string(self, string):
        try: # attempt to split the string into a module and attribute
            module_name, decorator_name = string.split(".")
        except ValueError: # there was no ".", it's just a single attribute
            module_name = "__main__"
            decorator_name = string
        finally:
            return module_name, decorator_name

    def _get_module(self, module_name):
        try: # attempt to load the module if it exists already
            module = sys.modules[module_name]
        except KeyError: # import it if it doesn't
            module = __import__(module_name)
        finally:
            return module

    def _get_decorator(self, decorator_name, module_name):
        module = self._get_module(module_name)
        return getattr(module, decorator_name)
        
"""        args, varargs, keyword_args, default_args = inspect.getargspec(function)
        
        args[0] = "self.function.im_self"
        template = self.regular_template
        header_size = "{}, " * len(args)
        header_args = [arg for arg in args]
        call_args = copy(header_args)
        call_size = header_size
        
        if default_args:
            new_args = []
            for arg in default_args:
                if isinstance(arg, str):
                    new_arg = repr(arg)
                else:
                    new_arg = arg
                new_args.append(new_arg)
            default_args = new_args
            non_defaults = len(args) - len(default_args)
            len(default_args)
            header_args = header_args[:non_defaults] + ["{}={}".format(arg_name, default_args[index]) for index, arg_name in enumerate(header_args[non_defaults:])]
            
        if varargs:
            header_size += "{}, "
            header_args.append("*"+varargs)
            template = self.varargs_template        
        
        if keyword_args:
            header_size += "{}, "
            header_args.append("**" + keyword_args)
            #print "increasing call size by 1", call_size
            call_size += "{}, "
           # print "call size is now", call_size
            call_args.append("**" + keyword_args)
            
        else:
            header_size += "{}, " * 3
            header_args.extend(("monkey_patch=None", "decorator=None", "decorators=None"))        
            
        ending = header_size.rfind(", ")
        header_size = header_size[:ending]
        
        ending = call_size.rfind(", ")
        call_size = call_size[:ending]
        
        self.header_size = header_size
        self.header_args = header_args
     #   print header_size, header_args
      #  print "header: {}".format(header_size).format(*header_args)
       # print "call sig: {}".format(call_size).format(*call_args)
        template = template.format(header_size).format(*header_args)
        template = template.replace("self.function.im_self", "self", 1)
        
        call_template = self.call_template.format(call_size).format(*call_args)
        
        ready_template = self.template = template + call_template
        new_code = compile(ready_template, "Runtime_Decorator.__call__ compile", 'exec')

        results = {}
        exec new_code in locals(), results
        self.__call__  = results.pop("__call__")
        
        #print self, "__call__ is ", self.__call__()
        print "created custom call signature for", function.func_name
        if function.func_name == "attribute_setter":
            print call_args, call_size
            print call_template
            print inspect.getargspec(self.__call__)
            print ready_template
     
    def __call__(self):
        raise NotImplementedError"""        