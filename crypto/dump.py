import sys

with open("dump.txt", 'w') as _file:
    _file.write(sys.stdin.read())