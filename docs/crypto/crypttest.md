crypto.crypttest
==============

 A standalone module to demo an authenticated feistel network built from a prf 

crypt_data
--------------

**crypt_data**(data, key, tag, constant_selector, direction, rounds, constants):

		 Feistel network based which uses permute as the round function.
        Functions as a basic feistel network, with some extra details:
            
            - Uses fused loops when loading buffers/applying the prf
            - 2 Key bytes operate on each data byte
            - The prf contributes to the creation of an authentication tag            
            - Internal round keys are different for any given message 
            - Tweakable constants parameter: one 16 bit word per round
                
        The key schedule is online and requires no up front preprocessing.
        This is an advantage to embedded devices, but a drawback to general purpose CPUs.
        
        Encryption produces an authentication tag, regardless of the mode of
        operation used.

        Recommended keysize: >= 256 bits. This stems from the size requirements
        of the authentication tag, which in general should be at least 128 bits
        to avoid the possibility of tag collisions. 
        
        An N bit key requires an N bit data input. So a 256 bit key operates
        upon data blocks of 256 bits in size. Half of the data generated
        each round is for plaintext/ciphertext data, while the other half
        is key material for the tag. 
        
        Number of rounds is configurable. A bare minimum of 3 are required to 
        at least obtain proper diffusion. 
        
        Each encryption uses a tweakable set of round constants. There should
        be one 16-bit constant per round. 
        
        The constant_selector variable is set to 0 for encryption, and to
        rounds - 1 for decryption.
        
        Likewise, the direction variable is set to 1 for encryption, and to
        -1 for decryption. 


crypt_data_test
--------------

**crypt_data_test**():

				No documentation available


decrypt_block
--------------

**decrypt_block**(data, key, tag, rounds, constants):

				No documentation available


encrypt_block
--------------

**encrypt_block**(data, key, rounds, constants):

				No documentation available


permutation
--------------

**permutation**(data, key, modifier):

		 Permutes all of the bytes in data in succession, from right to left,
        with wrap around, using the supplied key and modifier. 
        
        For more information, please see the documentation for the permute 
        function. 


permute
--------------

**permute**(left_byte, right_byte, key_byte, modifier):

		 Psuedorandom function. left_byte, right_byte, and key_byte are all
        16-bit unsigned integers. 
        
        psuedo code:
            
            right_byte += key_byte + modifier
            left_byte += right_byte >> 8
            left_byte ^= rotate_right(right_byte, 3)
            
        The basic idea is to view the left and right bytes as two wheels on a 
        simple combination lock. The right wheel is incremented by an amount,
        and if the amount "wraps around", then the left wheel is incremented
        by an amount as well. For example:
            
            [(0, 0), (0, 1), (0, 2), (0, 3), ... (0, 8), (0, 9), (1, 0), (1, 1), ...]
            
        Except, in this function, the "wrap around" effect is achieved via
        overflow into the high order byte instead of addition modulo 256. 
        Any overflow is added to the byte to the left.
        
        After the overflow is added to the left byte, the right byte is rotated
        by an amount and combined with the left via bitwise exclusive or. This
        helps add nonlinearity to the transformation. 
        
        This function was intended to be applied on a sequence of bytes, from
        the right to the left; At the end, when the 0th index is being supplied
        as the right_byte, the -1 index should be taken to mean the last byte
        of data, on the right. This wraps the effects of the permutation around
        to the other side. Two rounds are typically required to achieve full 
        diffusion. 


permute_subroutine
--------------

**permute_subroutine**(data, key, index, modifier):

		 Helper function 


xor_sum
--------------

**xor_sum**(data1):

				No documentation available
