#include <stdio.h>

int xor_sum(char* data, int end_of_data)
{
    int index;
    int result = 0;    
    for (index = 0; index < end_of_data; index = index + 1){        
        result ^= data[index];
        }
    return result;
}
    
// from http://stackoverflow.com/questions/213042/how-do-you-do-exponentiation-in-c    
long modular_exponentiation(long x, unsigned n, int modulus)
{
    long  p;
    long  r;
    long backup = n;
    
    p = x;
    r = 1.0;
    while (n > 0)
    {
        if (n % 2 == 1)
            r *= p;
        p *= p;
        n /= 2;
    }
    printf("%d ** %d = %d\n", x, backup, r);
    return(r % modulus);
}

char* generate_s_box()
{
    int index, value;
    char S_BOX[256];
    char* result = NULL;
    result = S_BOX;
    for (index=0; index < 256; index ++)
    {
        value = modular_exponentiation(251, index, 257) % 256;
        S_BOX[index] = value;        
    }
    return result;
}
    
void substitution(char* data, char* key, char* times, char* space, char* S_BOX, int size_of_data)
{
    int state, data_xor, key_xor, index, time, place, random_place;
    int time_constant = 1;
    data_xor = xor_sum(data, sizeof(data));
    key_xor = xor_sum(key, sizeof(key));
    state = data_xor ^ key_xor;
    for (index = 0; index < size_of_data; index ++)
    {
        time = times[index];
        place = space[index];
        time_constant = S_BOX[time];
        
        random_place = S_BOX[key[place] ^ time_constant] % size_of_data;     
                        
        state ^= data[random_place];
        data[random_place] ^= S_BOX[state ^ random_place];
        state ^= data[random_place];
                
        state ^= data[place];
        data[place] ^= S_BOX[state ^ S_BOX[place] ^ time_constant];
        state ^= data[place];
                        
        state ^= data[random_place];
        data[random_place] ^= S_BOX[state ^ random_place];
        state ^= data[random_place];
    }
}
    
int main () {
    char data[8] = "Testing ";
    char key[8] = "Testing ";
    int output;    
    output = xor_sum(data, sizeof(data));
    printf("Data: %s\n", data);
    printf("xor sum of data: %d\n", output);
 
    char* S_BOX;
    S_BOX = generate_s_box();
    int index;
    for (index = 0; index < 256; index++)
    {
        printf("Sbox %d = %c\n", index, S_BOX[index]);
    }        
        
    char times[8], space[8];
    for (index = 0; index < 8; index ++)
    {
        times[index] = index;
        space[index] = index;
    }
    
    printf("Data before: %s\n", data);
    substitution(data, key, times, space, S_BOX, sizeof(data));
    printf("Data after : %s\n", data);
    
    return 0;
}        