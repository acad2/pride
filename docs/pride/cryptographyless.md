pride.cryptographyless
==============

 Provides authenticated encryption and decryption functions using only the python standard library.
    To be used in situations where the cryptography module cannot be installed, usually for permission reasons. 

HKDFExpand
--------------

	No documentation available


Method resolution order: 

	(<class 'pride.cryptographyless.HKDFExpand'>, <type 'object'>)

- **derive**(self, key_material):

				No documentation available


Hash_Object
--------------

	No documentation available


Method resolution order: 

	(<class 'pride.cryptographyless.Hash_Object'>, <type 'object'>)

- **finalize**(self):

				No documentation available


InvalidTag
--------------

	No documentation available


Method resolution order: 

	(<class 'pride.errors.InvalidTag'>,
	 <class 'pride.errors.SecurityError'>,
	 <type 'exceptions.Exception'>,
	 <type 'exceptions.BaseException'>,
	 <type 'object'>)

Key_Derivation_Object
--------------

	No documentation available


Method resolution order: 

	(<class 'pride.cryptographyless.Key_Derivation_Object'>, <type 'object'>)

- **derive**(self, kdf_input):

				No documentation available


apply_mac
--------------

**apply_mac**(key, data, algorithm, backend):

				No documentation available


decrypt
--------------

**decrypt**(packed_encrypted_data, key, mac_key, backend):

		 Decrypts packed encrypted data as returned by encrypt with the same key. 
        If extra data is present, returns plaintext, extra_data. If not,
        returns plaintext. Raises InvalidTag on authentication failure. 


encrypt
--------------

**encrypt**(data, key, mac_key, iv, extra_data, algorithm, mode, backend, iv_size, hash_algorithm):

				No documentation available


generate_mac
--------------

**generate_mac**(key, data, algorithm, backend):

				No documentation available


hash_function
--------------

**hash_function**(algorithm_name, backend):

				No documentation available


hkdf_expand
--------------

**hkdf_expand**(algorithm, length, info, backend):

		 Returns an hmac based key derivation function (expand only) from
        cryptography.hazmat.primitives.hkdf. 


key_derivation_function
--------------

**key_derivation_function**(salt, algorithm, length, iterations, backend):

				No documentation available


load_data
--------------

**load_data**(packed_data):

				No documentation available


psuedorandom_bytes
--------------

**psuedorandom_bytes**(key, seed, count, hash_function):

		 usage: psuedorandom_bytes(key, seed, count, 
                                  hash_function="SHA256") => psuedorandom bytes
                
        Generates count cryptographically secure psuedorandom bytes. 
        Bytes are produced deterministically based on key and seed, using 
        hash_function with _hmac_rng. 


random_bytes
--------------

**random_bytes**(count):

		 Generates count cryptographically secure random bytes 


save_data
--------------

**save_data**(args):

				No documentation available


test__encrypt__decrypt
--------------

**test__encrypt__decrypt**():

				No documentation available


test_encrypt_decrypt
--------------

**test_encrypt_decrypt**():

				No documentation available


test_hmac_rng
--------------

**test_hmac_rng**():

				No documentation available


verify_mac
--------------

**verify_mac**(key, packed_data, algorithm, backend):

		 Verifies a message authentication code as obtained by apply_mac.
        Successful comparison indicates integrity and authenticity of the data. 
