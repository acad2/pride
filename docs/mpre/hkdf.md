mpre.hkdf
==============

 A python implementation of hmac-based extract-and-expand key derivation function (HKDF).
    
    usage:
        
        hkdf.hkdf(input_keying_material, length, info='', salt='', hash_function=DEFAULT_HASH)
        
        or
        
        key_deriver = hkdf.HKDF(hash_function=DEFAULT_HASH)
        key_deriver.hkdf(input_keying_material, length, info='', salt='')
         
    From http://tools.ietf.org/html/rfc5869 :
        
        A key derivation function (KDF) is a basic and essential component of
        cryptographic systems.  Its goal is to take some source of initial
        keying material and derive from it one or more cryptographically
        strong secret keys.

HKDF
--------------

	No documentation available


Method resolution order: 

	(<class 'mpre.hkdf.HKDF'>, <type 'object'>)

- **expand**(self, psuedorandom_key, length, info):

				No documentation available


- **extract**(self, input_keying_material, salt):

				No documentation available


- **hkdf**(self, input_keying_material, length, info, salt):

				No documentation available


expand
--------------

**expand**(psuedorandom_key, length, hash_length, info, hash_function):

				No documentation available


extract
--------------

**extract**(input_keying_material, salt, hash_function):

				No documentation available


hkdf
--------------

**hkdf**(input_keying_material, length, info, salt, hash_function):

				No documentation available
