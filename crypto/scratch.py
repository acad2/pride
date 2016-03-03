def bit_shuffle(data, key, indices):
    for index in indices:
        data = rotate(data[:index], key[index]) + data[index:]
    return data