
import os

cmd = 'gcc -Wall -Wextra -O3 -ansi -std=c99 -pedantic ' + \
      '-shared crc8.c -o crc8.dll'

print( cmd, '\nres: ', os.system(cmd) )
