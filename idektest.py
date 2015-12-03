import random

def generate_random_numbers(amount=128):
    numbers = set()
    while len(numbers) < amount:
        numbers.update([random._urandom(1) for x in xrange(amount)])
    return set([ord(char) for char in (numbers)][:amount])

server_numbers = generate_random_numbers()
client_numbers = generate_random_numbers()

shared_numbers = server_numbers.intersection(client_numbers)
sorted_numbers = sorted(list(shared_numbers))

#print "Client numbers: ", sorted(list(client_numbers))
#print "Match numbers : ", sorted_numbers

def xor_together(numbers):
    _xor = 0
    for number in client_numbers:
        _xor ^= number
    return _xor
    
client_xor = xor_together(client_numbers)
server_xor = xor_together(server_numbers)
# (1 ^ 3 ^ 5) ^ (2 ^ 3 ^ 5) = (1 ^ 2)
disjunction = server_xor ^ client_xor

# (1 ^ 2) ^ (2 ^ 3 ^ 5)
shared_numbers = disjunction ^ server_xor    
#shared_numbers = (3 ^ 5)
for number in server_numbers:
    if client_shared_secrets


def find_run(numbers, spacing=4):
    run = []    
    longest_run = 0
    last_index = len(numbers) - 1
    starts_at = None
    for index, number in enumerate(numbers):      
        if index == last_index:
            if run and numbers[index - 1] + spacing >= number:
                run.append(number)
                longest_run = len(run)
                run_start = starts_at
            break
        if number + spacing >= numbers[index + 1]:
            if not starts_at:
                starts_at = index
            run.append(number)
        else:
            if len(run) > longest_run:
                longest_run = len(run)
                run_start = starts_at
            run = []
            starts_at = None
    return run_start, longest_run
 
def test_runs()
    runs = dict((x, 0) for x in xrange(128))
    print_counter = 0 
    import pprint
    while True:
        length = 0
        client_numbers = generate_random_numbers()
        while length < 16:
            server_numbers = generate_random_numbers()    
            shared_numbers = server_numbers.intersection(client_numbers)
            sorted_numbers = sorted(list(shared_numbers))
            start, length = find_run(sorted_numbers)
        runs[length] += 1
        print_counter += 1
        if print_counter == 100:
            print_counter = 0
            pprint.pprint(runs)
            raw_input("waiting...")