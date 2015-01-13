name = 'Harsdenwood'

description = '''
	In the middle of the day, the woods are pleasant.  Birds are chirping away,
	streaks of sunlight make their way through the loose canopy above.

	The creek continues to the south into what could be a clearing.

	There is a trap door that is poorly disguised to look like a tree stump
	partially obscured by some bushes.
'''

exits = {
    'north': 'src.story.town_center',
    'south': 'src.story.clearing',
}

def open(origin, what=None, *args):
	if not what:
		origin.write('You seem to be on the right track, but not quite there.')
		return True, ''

	if what.lower() in ('door', 'trap'):
		origin.write('You successfully open the trap door stump. There is a ladder going down.')
		exits['down'] = 'src.story.cave'
		origin.add_xp('opening the trap door', 359)

	return True, ''



