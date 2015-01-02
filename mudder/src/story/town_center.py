from ..server.enums import UserStatus

is_start = True

name = "Town Square"
description = '''
This is the middle of the town. There is a fountain gurgling away within a pool.
'''
exits = {
    'north': 'tavern'
}

def swim(origin):
    origin.set_status(UserStatus.wet, True)
    origin.call_after(60*2, lambda: dryoff(origin))
    origin.write('You jump into the fountain and swim around.')

def dryoff(origin):
    origin.set_status(UserStatus.wet, False)
    origin.write('You dried off')
