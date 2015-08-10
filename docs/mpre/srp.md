mpre.srp
==============


  A python implementation of the secure remote password protocol for the
  metapython runtime environment. Authenticated_Service and
  Authenticated_Client objects default to using SRP for authentication, 
  and in most cases those objects will be used instead of the
  Secure_Remote_Password objects directly.
  
  N, g, and the hash function are customizable. Simply specify them
  as defaults or manually to the constructor. Note that for the protocol
  to operate successfully, both client and server must use the same values
  for N, g, and the hash function.
  
  The following table has been adopted with an adjustment to fit 
  pythons syntax. ^ is originally used to indicate modular exponentiation
  but is implemented in python via the pow function, while in python
  ^ means XOR.
  
  - N:    A large safe prime (N = 2q+1, where q is prime). All arithmetic is done modulo N.
  - g:    A generator modulo N
  - k:    Multiplier parameter (k = H(N, g) in SRP-6a, k = 3 for legacy SRP-6)
  - s:    User's salt
  - I:    Username
  - p:   Cleartext Password
  - H:  One-way hash function
  - ^:    XOR
  - pow: (Modular) Exponentiation
  - u:    Random scrambling parameter
  - a,b:  Secret ephemeral values
  - A,B:  Public ephemeral values
  - x:   Private key (derived from p and s)
  - v:    Password verifier

InsecureValueError
--------------

	No documentation available


Method resolution order: 

	(<class 'mpre.srp.InsecureValueError'>,
	 <type 'exceptions.Warning'>,
	 <type 'exceptions.Exception'>,
	 <type 'exceptions.BaseException'>,
	 <type 'object'>)

SRP_Client
--------------

	 Provides the client side of the secure remote password protocol. 


Instance defaults: 

	{'N': 7773717265111716665784849108811195468691168212183666610943831201085010511899891097866548572111118684910952747912290758810072831034786508356106531131032323232323232325611098525085112495510589108117801138466120747252577412211182113995110871785281116105831038189734868755710010789108857374991131001088911699101102104727210323232323232323211955104881167972798468120541021026590977312056106506610810911681659072113836688821124885121521208012110288777210098804868651036967L,
	 '_deleted': False,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'g': 2,
	 'hash_function': <function _hash_function at 0x02440FB0>,
	 'password': '',
	 'replace_reference_on_load': True,
	 'thread': None,
	 'username': ''}

Method resolution order: 

	(<class 'mpre.srp.SRP_Client'>, <class 'mpre.base.Base'>, <type 'object'>)

- **initial_message**(self):

		 Returns the username and A value required to initiate login. 


- **verify_proof**(self, response):

		 Verifies the servers proof of the shared secret against the
            one calculated by the client. 


- **login**(self, response):

		 Advances the login process 


- **handle_challenge**(self, response):

		 Calculates and returns the shared secret and proof of it. 


Secure_Remote_Password
--------------

	 Provides the server side for the secure remote password protocol. 


Instance defaults: 

	{'N': 7773717265111716665784849108811195468691168212183666610943831201085010511899891097866548572111118684910952747912290758810072831034786508356106531131032323232323232325611098525085112495510589108117801138466120747252577412211182113995110871785281116105831038189734868755710010789108857374991131001088911699101102104727210323232323232323211955104881167972798468120541021026590977312056106506610810911681659072113836688821124885121521208012110288777210098804868651036967L,
	 '_deleted': False,
	 'database_filename': 'user_registry',
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'g': 2,
	 'hash_function': <function _hash_function at 0x02440FB0>,
	 'new_salt': <function new_salt at 0x02479070>,
	 'replace_reference_on_load': True}

Method resolution order: 

	(<class 'mpre.srp.Secure_Remote_Password'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **on_load**(self, attributes):

				No documentation available


- **new_verifier**(self, username, password):

		 Creates a new password verifier for the specified username 
            and password. Note that no database interactions take place,
            and it is the callers responsibility to ensure that username
            does not already exist. 


- **login**(self, username, response, salt, verifier):

		 Advances the login process 


new_salt
--------------

**new_salt**(size):

				No documentation available


random_bits
--------------

**random_bits**(n):

				No documentation available


test_srp
--------------

**test_srp**():

				No documentation available
