int xor_subroutine(unsigned char* state, unsigned char* state2);

int xor_sum(unsigned char* state);

unsigned char rotate_left(unsigned char x, unsigned char r);

int shuffle_bytes(unsigned char* state);

int p_box(unsigned char* state);

unsigned char permute(unsigned char* state, unsigned char round_key, unsigned char key_byte, unsigned char left_index, unsigned char right_index);

int encrypt(unsigned char* state, unsigned char* key, unsigned int rounds);

unsigned char invert_permute(unsigned char* state, unsigned char round_key, unsigned char key_byte, unsigned int left_index, unsigned int right_index);

int invert_shuffle_bytes(unsigned char* state);

int decrypt(unsigned char* state, unsigned char* key, unsigned int rounds);