from ..server.enums import UserStatus

name = 'Harsden Beach'

description = 'The beach.'

exits = {
	'east': 'src.story.town_center',
}

def swim(origin):
    origin.set_status(UserStatus.wet, True)
    origin.add_xp('swimming in the lake', 147)
    origin.call_after(60*2, lambda: dryoff(origin))
    origin.write('You jump into the lake and swim around.')

def dryoff(origin):
    origin.set_status(UserStatus.wet, False)
    origin.add_xp('drying off', 3)
    origin.write('You dried off')
