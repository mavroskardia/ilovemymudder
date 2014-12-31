from ..server.enums import UserStatus


name = "Town Square"
is_start = True
description = '''
This is the middle of the town. There is a fountain gurgling away within a pool.

There is a tavern to the north.
'''

def swim(origin):
    origin.set_status(UserStatus.wet, True)
    origin.call_after(60*5, lambda: dryoff(origin))
    origin.write('You jump into the fountain and swim around.')

def dryoff(origin):
    origin.set_status(UserStatus.wet, False)
    origin.write('You dried off')
