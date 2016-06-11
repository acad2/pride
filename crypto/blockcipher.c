#include <stdlib.h>
#include <stdio.h>
#include <string.h>
void print_data(unsigned char* data)
{
    int index;
    printf("\n");
    for (index = 0; index < 16; index++)
    {
        printf("%i: %i\n", index, data[index]);
    }
}   

unsigned char rotate_left(unsigned char byte, int amount)
{    
    return ((byte << amount) | (byte >> (8 - amount))) & 255;
}

unsigned char rotate_right(unsigned char byte, int amount)
{              
    return ((byte >> amount) | (byte << (8 - amount))) & 255;
}

int prp(unsigned char* data, unsigned char key, unsigned char data_size)
{
    unsigned char index, byte;
    for (index = 0; index < data_size; index++)
    {    
        byte = data[index];
        key ^= byte;                       
        data[index] = rotate_left((byte + key + index) & 255, 5);        
        key ^= data[index]; 
    }
    return key;
}
        
int prf(unsigned char* data, unsigned char key, unsigned char data_size)
{
    unsigned char index, byte;
    for (index = 0; index < data_size; index++)
    {    
        byte = rotate_left((data[index] + key + index) & 255, 5);  
        key ^= byte;
        data[index] = byte;           
    }
}
    
unsigned char xor_with_key(unsigned char* data, unsigned char* key)
{
    unsigned char data_xor = 0, index;
    for (index = 0; index < 16; index++)
    {           
        data[index] ^= key[index];
        data_xor ^= data[index];
    }    
    return data_xor;
}

void encrypt(unsigned char* data, unsigned char* _key, int rounds)
{
    unsigned char key[16];
    unsigned char round_key[16], key_xor = 0, data_xor = 0, key_byte;
    int index, index2;
    for (index = 0; index < 16; index++)
    {
        key_byte = _key[index];
        key[index] = key_byte;
        key_xor ^= key_byte;                
        round_key[index] = 0;
        
        data_xor ^= data[index];
    }
    printf("Encrypting:\n");
    
    for (index = 0; index < rounds; index++)
    {                
        key_xor = prp(key, key_xor, 16); // generate key 
        memcpy(round_key, key, 16); // maintain invertible keyschedule                
        
        prf(round_key, key_xor, 16); // one way extraction: class '2B' keyschedule        
        
        data_xor = xor_with_key(data, round_key); // pre-whitening
        data_xor = prp(data, data_xor, 16); // high diffusion prp
        xor_with_key(data, round_key); // post-whitening
    }
}

unsigned char invert_prp(unsigned char* data, unsigned char key, int data_size)
{   
    unsigned char byte;
    int index;    
    for (index = data_size - 1; index != -1; index--)
    {                    
        byte = data[index];
        key ^= byte;                
        data[index] = (256 + (rotate_right(byte, 5) - key - index)) & 255;       
        key ^= data[index];
    }
    return key;
}
    
void decrypt(unsigned char* data, unsigned char* _key, int rounds)
{
    unsigned char key[16], round_key[16];
    unsigned char round_keys[16 * rounds];
    unsigned char key_xor = 0, data_xor = 0, key_byte;
    int index, index2;
    for (index = 0; index < 16; index++)
    {
        key_byte = _key[index];
        key_xor ^= key_byte;
        key[index] = key_byte;
        
        data_xor ^= data[index];
    }      
    
    for (index = 0; index < rounds; index++)
    {          
        key_xor = prp(key, key_xor, 16);        
        memcpy(round_key, key, 16);
                
        prf(round_key, key_xor, 16);
        memcpy(round_keys + (index * 16), round_key, 16);                
    }
    
    for (index = (rounds - 1); index != -1; index--)
    {            
        memcpy(round_key, round_keys + (index * 16), 16);
        
        data_xor = xor_with_key(data, round_key);         
        data_xor = invert_prp(data, data_xor, 16);
        xor_with_key(data, round_key);
    }
}
        
void test_encrypt_decrypt()
{
    unsigned char null_string[16] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};
    unsigned char data[16], key[16], plaintext[16];
    int rounds = 16, index;
    
    memcpy(data, null_string, 16);       
    data[15] = 1;
    memcpy(plaintext, data, 16);
    memcpy(key, null_string, 16); 
    
    encrypt(data, key, rounds);
    
    print_data(data);
        
    decrypt(data, key, rounds);
    print_data(data);
}

void main()
{
    test_encrypt_decrypt();    
}