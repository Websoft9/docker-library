#!/usr/bin/env python2
#!/usr/bin/env python3
from passlib.hash import nthash

input = open('/tmp/password','r')
a = input.read().replace("\n", "").replace("\r", "")
print(a)
h = nthash.hash(a)
print(h)

output = open('/tmp/password', 'w')
output.write(h)
output.close()