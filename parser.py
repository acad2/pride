class Parser(object):
    
    def get_string_indices(source):
        """ Return a list of indices of strings found in source. 
            Does not include strings located within other strings. """
        quotes = ["'", '"']
        start_index = end_index = 0
        triple_quote_start = triple_quote_end = ignore_count = 0
        source_length = len(source) - 1
        triple_quote_closing = closing_quote = ''
        indices = []
        for index, character in enumerate(source):
            _character = source[index:index + min(3, source_length - index)]
            if ignore_count:
                ignore_count -= 1
                continue
                
            if _character == "'''" or _character == '"""':
                if not start_index:
                    start_index = index
                    closing_quote = _character
                elif _character == closing_quote:
                    closing_quote = ''
                    end_index = index + 3
                    ignore_count = 2
                                    
            elif character in quotes:
                if not start_index:
                    start_index = index
                    closing_quote = character
                    
                elif character == closing_quote:
                    closing_quote = ''                
                    end_index = index + 1
                    
            if end_index:
                indices.append((start_index, end_index))
                start_index = end_index = 0 
                    
        return indices
        
    def find_symbol(symbol, source):
        strings = [range(start, end) for 
                   start, end in self.get_string_indices(source)]
        indices = []
        symbol_size = len(symbol)
        source_index = 0
        while symbol in source:
            start = source_index + source.index(symbol)
            for _range in strings:
                if start in _range:
                    end_of_quote = _range[-1]
                    source = source[end_of_quote:]
                    source_index += end_of_quote
                    break
            else: # did not break, symbol is not inside a quote
                end = start + symbol_size
                indices.append((start, end))
                source = source[end:]
                source_index += end
        return indices