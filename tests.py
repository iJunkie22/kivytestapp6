__author__ = 'ethan'
from collections import OrderedDict
import string

letters = [(x, i) for i, x in enumerate(string.ascii_lowercase)]

test1 = OrderedDict(letters)

test2 = OrderedDict(letters)
test2['b'] = 4

print test1
print test2
