#! /usr/bin/python -u

import sys

#
# Two functions that help dealing with ternary
#

# @memoize ?
def int2tri(x):
  """Int to ternary string representation"""
  nums="012"
  unjust = ((x == 0) and nums[0]) or (int2tri(x // 3).lstrip(nums[0]) + nums[x % 3])
  return "%s%s" % ("0" * (10 - len(unjust)), unjust)

def tri2int(x):
  """Ternary string representation to int."""
  return int(x, 3)


#
# Language instruction.
#
def rotr(x):
  """Rotate 1 trit right"""
  return tri2int("%s%s" % (int2tri(x)[-1:], int2tri(x)[:-1]))


def crazy(x, y):
  crz = [ ["1", "0", "0"], 
	      ["1", "0", "2"], 
	      ["2", "2", "1"] ]
  tri_x = int2tri(x)
  tri_y = int2tri(y)  
  out = []
  for cx, cy in zip(tri_x, tri_y):
    out.append(crz[int(cx)][int(cy)])
  return tri2int("".join(out))


def encrypt(x):
  enc_table = '''9m<.TVac`uY*MK'X~xDl}REokN:#?G"i@5z]&gqtyfr$(we4{WP)H-Zn,[%\\3dL+Q;>U!pJS72FhOA1CB6v^=I_0/8|jsb'''
  return ord(enc_table[x % 94])


def out(x):
  if x < 256:
    sys.stdout.write(chr(x))
  else:
    sys.stdout.write('U+%04x' % x)


def getch():
  """Actually called 'in', but reserved in python."""
  gotc = sys.stdin.read(1)
  if not gotc:
    return 59048
  return ord(gotc)

#
# File loading
#


#
# Main
#
class Malbolge_Interpreter(object):

    def __init__(self):
        self.a, self.c, self.d = (0, 0, 0)
        self.memory = [0] * 59049        
 
    def load_file(self, filename):
        memory = self.memory
        instrs = [4, 5, 23, 39, 40, 62, 68, 81]     
        
        with open(filename, "rb") as f:
            program = bytearray(f.read().replace(" ", ''))
            for index, character in enumerate(program):
                if (character + index) % 94 not in instrs:
                    print "Error loading program at address: {}".format(i)
                    memory[index] = character
                    
            for index in range(59048 - index):
                memory[index] = crazy(memory[index - 2], memory[index - 1])
                
            while True:
                c = f.read(1)
                if not c:
                    break
                if c.isspace():
                    continue
                if ((ord(c) + i) % 94) not in instrs:
                    print "Error loading program at address %i." % i
                    memory[i] = ord(c)
                    i += 1
            
        # Crazy Fill the rest of the memory
        while i <= 59048:
            memory[i] = crazy(memory[i-2], memory[i-1])
            i += 1
        
    def run(self, filename):
        a, c, d, memory = self.a, self.c, self.d, self.memory
        
        self.load_file(filename)  
        
        a = c = d = 0
        running = True
        while running:
            instruction = (memory[c] + c) % 94
            
            if instruction == 4:
                # jmp [d] + 1
                c = memory[d]
            elif instruction == 5:
                # out a
                out(a % 256)
            elif instruction == 23:
                # in a
                a = getch()
            elif instruction == 39:
                # rotr [d]
                # mov a, [d]
                memory[d] = rotr(memory[d])
                a = memory[d]
            elif instruction == 40:
                # mov d, [d]
                d = memory[d]
            elif instruction == 62:
                # crz [d], a
                # mov a, [d]
                a = crazy(memory[d], a)
                memory[d] = a
            elif instruction == 68:
                # nop
                pass
            elif instruction == 81:
                # end
                running = False
                # endif
        
            # advance
            if c == 59048:
                c = 0
            else:
                c += 1
            if d == 59048:
                d = 0
            else:
                d += 1
            
            # encrypt [c-1]
            memory[c-1] = encrypt(memory[c-1])
                 

if __name__ == "__main__":
    interpreter = Malbolge_Interpreter()
    interpreter.run("helloworld.malbolge")
    