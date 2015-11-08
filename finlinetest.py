class Function_Inliner(object):
    
  #  def handle_source(self, source):
  #      _source = []
  #      function_calls = []
  #      for line in source.split('\n'):
  #          for symbol in line.split():
  #              print "Checking for calls in: ", symbol
  #              while '(' in symbol:
  #                  print "Attempting to extracting name from: ", symbol
  #                  name, symbol = symbol.split('(', 1)
  #                  if name and ')' not in name and '[' not in name:
  #                      print "Success, adding name: ", name
  #                      function_calls.append(name)
  #      print function_calls
        
    def handle_source(self, source):
        function_calls = []
        for line in source.split('\n'):
            for symbol in line.split():
                while '(' in symbol:
                    name, symbol = symbol.split('(', 1)
                    if name and ')' not in name and '[' not in name:
                        function_calls.append(name)
        print function_calls        
def test():
    genexp = (x for x in xrange(100))
    genexp2 = (int(x / .1) for x in genexp)
    another_test = (float('1.1'), int('1'), ord('c'))
    
if __name__ == "__main__":
    function_inliner = Function_Inliner()
    import importers, base, inspect
    source = importers.Parser.extract_code(inspect.getsource(function_inliner.handle_source))
    function_inliner.handle_source(source)