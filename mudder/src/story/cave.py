name = 'Hole in the Ground'
description = '''
	You descend the ladder into the hole in the ground.

	As you set foot on the bottom rung of the ladder, the trapdoor above slams
	shut, leaving you in total darkness.
'''

exits = {
}

def light(origin, what=None, *args):
	if not what:
		origin.write('''
	Yeah, a light would be nice. Maybe you want to light one of the matches
	in your pocket?
''')
		return True, ''

	if what.lower() == 'match':
		msg = '''
	You light a match.  With the small amount of light given off, you can see
	there is a perfectly nice torch on the wall near you.
		'''
		origin.write(msg)
		origin.add_xp('lighting a match', 113)

	if what.lower() == 'torch':
		msg = '''
	You light the torch with another match.  Now you can see that you are in a
	cave that extends north back towards town.  The trapdoor above you has no
	means of opening from down here.
'''
		origin.write(msg)
		origin.add_xp('finding your way with the torch', 243)
		exits['north'] = 'src.story.undertown'

	return True, ''