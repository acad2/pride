classicalciphers
==============



Adfgvx_Cipher
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'key': ['8',
	         'p',
	         '3',
	         'd',
	         '1',
	         'n',
	         'l',
	         't',
	         '4',
	         'o',
	         'a',
	         'h',
	         '7',
	         'k',
	         'b',
	         'c',
	         '5',
	         'z',
	         'j',
	         'u',
	         '6',
	         'w',
	         'g',
	         'm',
	         'x',
	         's',
	         'v',
	         'i',
	         'r',
	         '2',
	         '9',
	         'e',
	         'y',
	         '0',
	         'f',
	         'q'],
	 'replace_reference_on_load': True,
	 'row_length': 5}

Method resolution order: 

	(<class 'classicalciphers.Adfgvx_Cipher'>,
	 <class 'classicalciphers.Array_Cipher'>,
	 <class 'classicalciphers.Cipher'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **test**(self):

				No documentation available


- **calculate_index**(self, pair):

				No documentation available


Array_Cipher
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'key': ['A',
	         'B',
	         'C',
	         'D',
	         'E',
	         'F',
	         'G',
	         'H',
	         'I',
	         'J',
	         'K',
	         'L',
	         'M',
	         'N',
	         'O',
	         'P',
	         'Q',
	         'R',
	         'S',
	         'T',
	         'U',
	         'V',
	         'W',
	         'X',
	         'YZ'],
	 'replace_reference_on_load': True,
	 'row_length': 5}

Method resolution order: 

	(<class 'classicalciphers.Array_Cipher'>,
	 <class 'classicalciphers.Cipher'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **decode**(self, encoded_message):

				No documentation available


- **test**(self):

				No documentation available


- **calculate_index**(self, integer_pair):

				No documentation available


Atbash_Cipher
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'cipher_key': 'ZYXWVUTSRQPONMLKJIHGFEDCBA',
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'plaintext_key': 'abcdefghijklmnopqrstuvwxyz',
	 'replace_reference_on_load': True}

Method resolution order: 

	(<class 'classicalciphers.Atbash_Cipher'>,
	 <class 'classicalciphers.Substitution_Cipher'>,
	 <class 'classicalciphers.Cipher'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **test**(self):

				No documentation available


Bacon_Cipher
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'cipher': {'AAAAA': 'a',
	            'AAAAB': 'b',
	            'AAABA': 'c',
	            'AAABB': 'd',
	            'AABAA': 'e',
	            'AABAB': 'f',
	            'AABBA': 'g',
	            'AABBB': 'h',
	            'ABAAA': 'j',
	            'ABAAB': 'k',
	            'ABABA': 'l',
	            'ABABB': 'm',
	            'ABBAA': 'n',
	            'ABBAB': 'o',
	            'ABBBA': 'p',
	            'ABBBB': 'q',
	            'BAAAA': 'r',
	            'BAAAB': 's',
	            'BAABA': 't',
	            'BAABB': 'v',
	            'BABAA': 'w',
	            'BABAB': 'x',
	            'BABBA': 'y',
	            'BABBB': 'z'},
	 'cipher_key': "axje.uidchtnmbrl'poygk,qf;",
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'plaintext_key': 'abcdefghijklmnopqrstuvwxyz',
	 'replace_reference_on_load': True}

Method resolution order: 

	(<class 'classicalciphers.Bacon_Cipher'>,
	 <class 'classicalciphers.Substitution_Cipher'>,
	 <class 'classicalciphers.Cipher'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **test**(self):

				No documentation available


Cipher
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'replace_reference_on_load': True}

Method resolution order: 

	(<class 'classicalciphers.Cipher'>, <class 'mpre.base.Base'>, <type 'object'>)

- **decode**(self, encoded_message):

				No documentation available


- **encode**(self, message):

				No documentation available


- **test**(self):

				No documentation available


Encryption_Scheme
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'replace_reference_on_load': True}

Method resolution order: 

	(<class 'classicalciphers.Encryption_Scheme'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **encrypt**(self, message):

				No documentation available


- **decrypt**(self, message):

				No documentation available


Equidistant_Letter_Sequence
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'interval': 1,
	 'replace_reference_on_load': True,
	 'start': 0}

Method resolution order: 

	(<class 'classicalciphers.Equidistant_Letter_Sequence'>,
	 <class 'classicalciphers.Cipher'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **decode**(self, encoded_message):

				No documentation available


- **crack**(self, message, dont_count_spaces, minimum_size):

				No documentation available


- **test**(self):

				No documentation available


Key_Rotation_Cipher
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'cipher_key': "axje.uidchtnmbrl'poygk,qf;",
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'plaintext_key': 'abcdefghijklmnopqrstuvwxyz',
	 'replace_reference_on_load': True,
	 'rotation_amount': 13}

Method resolution order: 

	(<class 'classicalciphers.Key_Rotation_Cipher'>,
	 <class 'classicalciphers.Substitution_Cipher'>,
	 <class 'classicalciphers.Cipher'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **rotate_key**(self, key, shift):

				No documentation available


- **test_crack**(self):

				No documentation available


- **crack**(self, encoded_message):

				No documentation available


- **test**(self):

				No documentation available


- **rotate_list_key**(self, key):

				No documentation available


Morse_Code
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'cipher': {'-': 't',
	            '--': 'm',
	            '---': 'o',
	            '-----': '0',
	            '----.': '9',
	            '---..': '8',
	            '--.': 'g',
	            '--.-': 'q',
	            '--..': 'z',
	            '--..--': ',',
	            '--...': '7',
	            '-.': 'n',
	            '-.-': 'k',
	            '-.--': 'y',
	            '-.-.': 'c',
	            '-..': 'd',
	            '-..-': 'x',
	            '-..-.': '/',
	            '-...': 'b',
	            '-....': '6',
	            '.': 'e',
	            '.-': 'a',
	            '.--': 'w',
	            '.---': 'j',
	            '.----': '1',
	            '.--.': 'p',
	            '.--.-.': '@',
	            '.-.': 'r',
	            '.-.-.-': '.',
	            '.-..': 'l',
	            '..': 'i',
	            '..-': 'u',
	            '..---': '2',
	            '..--..': '?',
	            '..-.': 'f',
	            '...': 's',
	            '...-': 'v',
	            '...--': '3',
	            '....': 'h',
	            '....-': '4',
	            '.....': '5'},
	 'cipher_key': "axje.uidchtnmbrl'poygk,qf;",
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'plaintext_key': 'abcdefghijklmnopqrstuvwxyz',
	 'replace_reference_on_load': True}

Method resolution order: 

	(<class 'classicalciphers.Morse_Code'>,
	 <class 'classicalciphers.Substitution_Cipher'>,
	 <class 'classicalciphers.Cipher'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **test**(self):

				No documentation available


Substitution_Cipher
--------------

	No docstring found


Instance defaults: 

	{'_deleted': False,
	 'cipher_key': "axje.uidchtnmbrl'poygk,qf;",
	 'delete_verbosity': 'vv',
	 'dont_save': False,
	 'plaintext_key': 'abcdefghijklmnopqrstuvwxyz',
	 'replace_reference_on_load': True}

Method resolution order: 

	(<class 'classicalciphers.Substitution_Cipher'>,
	 <class 'classicalciphers.Cipher'>,
	 <class 'mpre.base.Base'>,
	 <type 'object'>)

- **decode**(self, encoded_message):

				No documentation available


- **encode**(self, message):

				No documentation available


- **test**(self):

				No documentation available
