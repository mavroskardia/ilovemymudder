from ..server.enums import UserStatus

is_start = True

name = "Town Square"
description = '''
        This is the center of the town. There is a pond that appears man-made that
        drains into a creek heading south towards an impenetrable forest that
        you dare not enter. There is a shoddy looking arena nearby.
'''
exits = {
    'north': 'src.story.tavern',
    'south': 'src.story.forest',
    'east': 'src.story.arena',
}

def swim(origin):
    origin.set_status(UserStatus.wet, True)
    origin.add_xp('swimming in the pong', 147)
    origin.call_after(60*2, lambda: dryoff(origin))
    origin.write('You jump into the pond and swim around.')

def dryoff(origin):
    origin.set_status(UserStatus.wet, False)
    origin.add_xp('drying off', 3)
    origin.write('You dried off')
