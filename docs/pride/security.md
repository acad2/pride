pride.security
==============

 Provides security related functions such as encryption and decryption.
    Two backends are available: Ideally, the cryptography package has been
    installed, and that will be used. In situations where that is not feasible,
    usually due to permissions, the pride.cryptographyless module will be used
    instead. 

Cipher
--------------

	No documentation available


Method resolution order: 

	(<class 'cryptography.hazmat.primitives.ciphers.base.Cipher'>, <type 'object'>)

- **encryptor**(self):

				No documentation available


- **decryptor**(self):

				No documentation available


HKDF
--------------

	No documentation available


Method resolution order: 

	(<class 'cryptography.hazmat.primitives.kdf.hkdf.HKDF'>, <type 'object'>)

- **derive**(self, key_material):

				No documentation available


- **verify**(self, key_material, expected_key):

				No documentation available


HKDFExpand
--------------

	No documentation available


Method resolution order: 

	(<class 'cryptography.hazmat.primitives.kdf.hkdf.HKDFExpand'>, <type 'object'>)

- **derive**(self, key_material):

				No documentation available


- **verify**(self, key_material, expected_key):

				No documentation available


HMAC
--------------

	No documentation available


Method resolution order: 

	(<class 'cryptography.hazmat.primitives.hmac.HMAC'>, <type 'object'>)

- **finalize**(self):

				No documentation available


- **verify**(self, signature):

				No documentation available


- **copy**(self):

				No documentation available


- **update**(self, data):

				No documentation available


InvalidPassword
--------------

	No documentation available


Method resolution order: 

	(<class 'pride.errors.InvalidPassword'>,
	 <class 'pride.errors.SecurityError'>,
	 <type 'exceptions.Exception'>,
	 <type 'exceptions.BaseException'>,
	 <type 'object'>)

InvalidSignature
--------------

	No documentation available


Method resolution order: 

	(<class 'cryptography.exceptions.InvalidSignature'>,
	 <type 'exceptions.Exception'>,
	 <type 'exceptions.BaseException'>,
	 <type 'object'>)

InvalidTag
--------------

	No documentation available


Method resolution order: 

	(<class 'cryptography.exceptions.InvalidTag'>,
	 <type 'exceptions.Exception'>,
	 <type 'exceptions.BaseException'>,
	 <type 'object'>)

PBKDF2HMAC
--------------

	No documentation available


Method resolution order: 

	(<class 'cryptography.hazmat.primitives.kdf.pbkdf2.PBKDF2HMAC'>,
	 <type 'object'>)

- **derive**(self, key_material):

				No documentation available


- **verify**(self, key_material, expected_key):

				No documentation available


SecurityError
--------------

	No documentation available


Method resolution order: 

	(<class 'pride.errors.SecurityError'>,
	 <type 'exceptions.Exception'>,
	 <type 'exceptions.BaseException'>,
	 <type 'object'>)

apply_mac
--------------

**apply_mac**(key, data, algorithm, backend):

		 Generates a message authentication code and prepends it to data.
            Mac and data are packed via pride.utilities.save_data. 
            
            Applying a message authentication code facilitates the goals
            of authenticity and integrity. Note it does not protect
            confidentiality (i.e. encryption).
            
            Combining a mac with encryption is NOT straightforward;
            Authenticating/providing integrity of confidential data
            should preferably be accomplished via an appropriate
            block cipher mode of operation, such as GCM. If this is
            not possible, encrypt-then-mac is most secure solution in
            general. 


decrypt
--------------

**decrypt**(packed_encrypted_data, key, mac_key, backend):

		 Decrypts packed encrypted data as returned by encrypt with the same key. 
            If extra data is present, returns plaintext, extra_data. If not,
            returns plaintext. Raises InvalidTag on authentication failure. 


encrypt
--------------

**encrypt**(data, key, mac_key, iv, extra_data, algorithm, mode, backend, iv_size, hash_algorithm, return_mode):

		 Encrypts data with the specified key. Returns packed encrypted bytes.
            If an iv is not supplied a random one of iv_size will be generated.
            By default, the GCM mode of operation is used and the iv is 
            automatically included in the extra_data authenticated by the mode. 
            
            Note that not all algorithms may support all modes of operation
            with all backends. 
            
            A mac key is required when GCM mode is not in used. This function
            will refuse to encrypt data without authentication/integrity checks,
            as this is considered a serious flaw in security. 
            
            Technically speaking, 'iv' is not always the correct term for the
            parameter passed, depending on the mode of operation used. However,
            using two different fields for what are functionally the same would
            increase complexity needlessly. 


generate_mac
--------------

**generate_mac**(key, data, algorithm, backend):

		 Returns a message authentication code for verifying the integrity and
            authenticity of data by entities that possess the key. 
            
            Note this is a lower level function then apply_mac and
            only returns the mac itself. 
            
            The mac is generated via HMAC with the specified algorithm and key. 


hash_function
--------------

**hash_function**(algorithm_name, backend):

		 Returns a Hash object of type algorithm_name from 
            cryptography.hazmat.primitives.hashes 


hkdf_expand
--------------

**hkdf_expand**(algorithm, length, info, backend):

		 Returns an hmac based key derivation function (expand only) from
            cryptography.hazmat.primitives.hkdf. 


key_derivation_function
--------------

**key_derivation_function**(salt, algorithm, length, iterations, backend):

		 Returns an key derivation function object from
            cryptography.hazmat.primitives.kdf.pbkdf2 


load_data
--------------

**load_data**(packed_data):

				No documentation available


random_bytes
--------------

**random_bytes**(count):

		 Generates count cryptographically secure random bytes 


save_data
--------------

**save_data**(args):

				No documentation available


test_packed_encrypted_data
--------------

**test_packed_encrypted_data**():

				No documentation available


verify_mac
--------------

**verify_mac**(key, packed_data, algorithm, backend):

		 Verifies a message authentication code as obtained by apply_mac.
            Successful comparison indicates integrity and authenticity of the data. 
            Returns data is comparison succeeds; Otherwise returns pride.security.INVALID_TAG. 
