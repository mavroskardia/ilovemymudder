name = 'Clearing in the woods'

description = '''
	You are in a small clearing in the Harsdenwood.  The clearing appears
	natural, but it isn't clear what keeps the trees from growing here.

	In the absolute center of the clearing someone has erected a pedastal.  On
	the pedastal is a small symbol that appears burned into the surface.

	The creek continues even further south into dense, neverending forest.
'''

exits = {
	'north': 'src.story.forest',
	'south': 'src.story.denseforest',
}

def touch(origin, what=None, *args):
	if not what:
		origin.write('''What, exactly, are you trying to touch?''')
		return True, ''

	if what.lower() == 'symbol':
		origin.write('''
	As you place your hand upon the symbol, a strange surge of energy courses
	through your body.  You feel stronger, wiser, and faster.
''')
		origin.add_xp('touching the strange symbol', 501)
	else:
		origin.write('''I don't know how to touch that.''')

	return True, ''
