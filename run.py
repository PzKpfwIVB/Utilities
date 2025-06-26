# Basic test for the installation
from utils_qt_mk._general import BijectiveDict
from utils_qt_mk.creators import creator_centre

bd_int_str = BijectiveDict(int)
bd_int_str[1] = 'one'
bd_int_str[2] = 'two'
bd_int_str[3] = 'three'

print(bd_int_str.keys(), bd_int_str.values())
print(bd_int_str['one'], bd_int_str['two'], bd_int_str['three'])

creator_centre()
