crypto.blockcipher
==============



Test_Cipher
--------------

	No documentation available


Method resolution order: 

	(<class 'crypto.blockcipher.Test_Cipher'>,
	 <class 'pride.crypto.Cipher'>,
	 <type 'object'>)

- **encrypt_block**(self, plaintext, key, tag, tweak):

				No documentation available


- **encrypt**(self, data, iv, tag, tweak):

				No documentation available


- **decrypt_block**(self, ciphertext, key, tag, tweak):

				No documentation available


- **decrypt**(self, data, iv, tag, tweak):

				No documentation available


Test_Embedded_Decryption_Cipher
--------------

	No documentation available


Method resolution order: 

	(<class 'crypto.blockcipher.Test_Embedded_Decryption_Cipher'>,
	 <class 'crypto.blockcipher.Test_Cipher'>,
	 <class 'pride.crypto.Cipher'>,
	 <type 'object'>)

- **decrypt_block**(self, ciphertext, key, tag, tweak):

				No documentation available


attack
--------------

**attack**():

				No documentation available


cast
--------------

**cast**(input_data, _type):

				No documentation available


decrypt_block
--------------

**decrypt_block**(ciphertext, key, rounds, tweak):

				No documentation available


decrypt_block_embedded_decryption_key
--------------

**decrypt_block_embedded_decryption_key**(ciphertext, final_round_key, rounds, tweak):

				No documentation available


encrypt_block
--------------

**encrypt_block**(plaintext, key, rounds, tweak):

				No documentation available


extract_round_key
--------------

**extract_round_key**(key):

		 Non invertible round key extraction function. 


generate_default_constants
--------------

**generate_default_constants**(block_size):

				No documentation available


generate_embedded_decryption_key
--------------

**generate_embedded_decryption_key**(key, rounds, tweak):

				No documentation available


generate_round_key
--------------

**generate_round_key**(key, constants):

		 Invertible round key generation function. 


generate_round_keys
--------------

**generate_round_keys**(key, rounds, tweak):

				No documentation available


generate_s_box
--------------

**generate_s_box**(function):

				No documentation available


online_keyschedule
--------------

**online_keyschedule**(data, key, constants, rounds, counter, state):

				No documentation available


online_keyschedule_embedded_decryption_key
--------------

**online_keyschedule_embedded_decryption_key**(data, key, constants, rounds, counter, state):

				No documentation available


shuffle
--------------

**shuffle**(data, key):

				No documentation available


shuffle_extract
--------------

**shuffle_extract**(data, key, state):

				No documentation available


slide
--------------

**slide**(iterable, x):

		 Yields x bytes at a time from iterable 


substitute_bytes
--------------

**substitute_bytes**(data, key, round_constants, counter, state):

		 Substitution portion of the cipher. Classifies as an even, complete,
        consistent, homeogenous, source heavy unbalanced feistel network. (I think?)
        (https://www.schneier.com/cryptography/paperfiles/paper-unbalanced-feistel.pdf)
        The basic idea is that each byte of data is encrypted based off 
        of every other byte of data around it.      
         
        Each byte is substituted, then a byte at a random location substituted,
        then the current byte substituted again. At each substitution, the output
        is fed back into the state to modify future outputs.
                        
        The ideas of time and spatial locality are introduced to modify how
        the random bytes are generated. Time is represented by the count of
        how many bytes have been enciphered so far. Space is indicated by the
        current index being operated upon.
        
        The S_BOX lookup could/should conceivably be replaced with a timing attack
        resistant non linear function. The default S_BOX is based off of
        modular exponentiation of 251 ^ x mod 257, which was basically
        selected at random and possesses a bad differential characteristic.

        The substitution steps are:
            
            - Remove the current byte from the state; If this is not done, the transformation is uninvertible
            - Generate an ephemeral byte to mix with the state; the ephemeral byte aims to preserve forward secrecy in
              the event the internal state is recovered (i.e. by differential attack)
            - Generate a psuedorandom byte from the state (everything but the current plaintext byte),
              then XOR that with current byte; then include current byte XOR psuedorandom_byte into the state 
            - This is done in the current place, then in a random place, then in the current place again. 


test_Cipher
--------------

**test_Cipher**():

				No documentation available


test_cipher_metrics
--------------

**test_cipher_metrics**():

				No documentation available


test_extract_round_key
--------------

**test_extract_round_key**():

				No documentation available


test_generate_round_key
--------------

**test_generate_round_key**():

				No documentation available


test_linear_cryptanalysis
--------------

**test_linear_cryptanalysis**():

				No documentation available


upfront_keyschedule
--------------

**upfront_keyschedule**(data, key, constants, rounds, counter, state):

				No documentation available


xor_subroutine
--------------

**xor_subroutine**(bytearray1, bytearray2):

				No documentation available


xor_sum
--------------

**xor_sum**(data):

				No documentation available
