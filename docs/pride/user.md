pride.user
==============



InvalidUsername
--------------

	No documentation available


Method resolution order: 

	(<class 'pride.user.InvalidUsername'>,
	 <type 'exceptions.BaseException'>,
	 <type 'object'>)

User
--------------

	 A User object for managing secure information and client accounts.
        A user is capable of performing manipulation of secure data,
        including encryption and decryption. The user object is responsible
        for deriving and holding keys required for such manipulation. 


Instance defaults: 

	{'deleted': False,
	 'dont_save': False,
	 'encryption_algorithm': 'AES',
	 'encryption_key': '',
	 'encryption_mode': 'GCM',
	 'file_system_key': '',
	 'hash_function': 'SHA256',
	 'hkdf_encryption_info_string': '{} Encryption Key',
	 'hkdf_file_system_info_string': '{} File_System key',
	 'hkdf_mac_info_string': '{} Message Authentication Code Key',
	 'iv_size': 12,
	 'kdf_iteration_count': 100000,
	 'key_length': 32,
	 'mac_key': '',
	 'open_command_line': True,
	 'parse_args': False,
	 'password_prompt': '{}: Please provide the pass phrase or word: ',
	 'replace_reference_on_load': True,
	 'salt': '',
	 'salt_filetype': 'pride.fileio.Database_File',
	 'salt_size': 16,
	 'startup_components': (),
	 'username': 'localhost',
	 'verifier_filetype': 'pride.fileio.Database_File',
	 'verifier_indexable': False}

Method resolution order: 

	(<class 'pride.user.User'>, <class 'pride.base.Base'>, <type 'object'>)

- **hash**(self, data):

		 Hash data using the user objects specified hashing algorithm 


- **decrypt**(self, packed_encrypted_data):

		 Decrypts packed encrypted data as returned by encrypt. The Users 
            encryption key is used to decrypt the data. 


- **verify**(self, macd_data):

		 Verifies data with the mac returned by authenticate. Data that is 
            verified has two extremely probable guarantees: that it did indeed
            come from who an authorized party, and that it was not manipulated 
            by unauthorized parties in transit. 
            
            Returns data on successful verification; Returns False on failure. 


- **authenticate**(self, data):

		 Returns tagged data.
            
            Authenticates and provides integrity to a piece of data. 
            Authentication and integrity are generally requirements for any data
            that must be secured. Returns a message authentication code.
            
            Note that User.encrypt uses AES-GCM mode, which authenticates
            data and extra_data automatically. 
            
            Combining encryption and authentication is not simple. This method 
            should be used ONLY in conjunction with unencrypted data, unless 
            you are certain you know what you are doing. 


- **encrypt**(self, data, extra_data):

		 Encrypt and authenticates the supplied data; Authenticates, but 
            does not encrypt, any extra_data. The data is encrypted using the 
            Users encryption key. Returns packed encrypted bytes. 
            
            Encryption is done via AES-256-GCM. 


- **load_data**(self, package):

				No documentation available


- **save_data**(self, *args):

				No documentation available


- **login**(self):

		 Attempt to login as username using a password. Upon success, the
            users encryption and mac key are derived and stored in memory.
            Upon failure, the prompt is repeated. 


- **generate_tag**(self, data):

		 Generates a unique, unforgeable tag based on supplied data. 


test_User
--------------

**test_User**():

				No documentation available
