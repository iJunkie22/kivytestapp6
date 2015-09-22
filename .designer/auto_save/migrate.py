__author__ = 'ethan'
import sys
import os

ex_path = sys.executable

#sym1 = os.path.join(ex_path, '../../../Frameworks/')
sym1 = '../../../Frameworks/'
sym2 = os.path.join(ex_path, '../Frameworks/')
test1 = os.path.dirname(sym1)
test2 = os.path.normpath(sym2)



print ex_path
print sym1
print sym2
print test1

print test2

os.symlink(test1, test2)
