bytecodedis
==============



Bytecode
--------------

No documentation available


- **get_block_info(self):

		No documentation available


- **create_paths(self):

		No documentation available


- **dump_co_info(self):

		No documentation available


- **get_jump_conditionss(self):

		No documentation available


- **display(self, co_vars):

		No documentation available


- **dump_opcodes(self):

		bytecode.dump_opcodes() => opcodes_list, block_list

        opcodes_list contains address, opcode, arg_address, arg tuples
        block_list contains block_address, block_code tuples


OrderedDict
--------------

Dictionary that remembers insertion order


- **keys(self):

		od.keys() -> list of keys in od


- **iteritems(self):

		od.iteritems -> an iterator over the (key, value) pairs in od


- **update(, *args, **kwds):

		 D.update([E, ]**F) -> None.  Update D from mapping/iterable E and F.
            If E present and has a .keys() method, does:     for k in E: D[k] = E[k]
            If E present and lacks .keys() method, does:     for (k, v) in E: D[k] = v
            In either case, this is followed by: for k, v in F.items(): D[k] = v
        


- **pop(self, key, default):

		od.pop(k[,d]) -> v, remove specified key and return the corresponding
        value.  If key is not found, d is returned if given, otherwise KeyError
        is raised.

        


- **viewkeys(self):

		od.viewkeys() -> a set-like object providing a view on od's keys


- **popitem(self, last):

		od.popitem() -> (k, v), return and remove a (key, value) pair.
        Pairs are returned in LIFO order if last is true or FIFO order if false.

        


- **copy(self):

		od.copy() -> a shallow copy of od


- **viewitems(self):

		od.viewitems() -> a set-like object providing a view on od's items


- **fromkeys(cls, iterable, value):

		OD.fromkeys(S[, v]) -> New ordered dictionary with keys from S.
        If not specified, the value defaults to None.

        


- **setdefault(self, key, default):

		od.setdefault(k[,d]) -> od.get(k,d), also set od[k]=d if k not in od


- **viewvalues(self):

		od.viewvalues() -> an object providing a view on od's values


- **items(self):

		od.items() -> list of (key, value) pairs in od


- **clear(self):

		od.clear() -> None.  Remove all items from od.


- **values(self):

		od.values() -> list of values in od


- **iterkeys(self):

		od.iterkeys() -> an iterator over the keys in od


- **itervalues(self):

		od.itervalues -> an iterator over the values in od


- **translator(statement):

		No documentation available
