name = 'Clive\'s Undertown'

description = '''
	You have entered into an underground market.
	There are musicians playing in the open areas around the various
	stalls.  Merchants and townspeople are haggling over the prices of food,
	clothing, and many sorts of raw materials used for crafting goods.

	You look up and see that there is a wide set of stairs carved into the
	far wall that can bring you back up to the surface level of the town.
'''

def onenter(origin, source):
	if source == 'src.story.cave':
		origin.write('''
	As you walk through the cave, you start to hear the sounds of music and
	bartering from the other side of a plain wooden door on the far side of the
	cave.

	You realize the door is a one-way secret entrance into the market as it
	closes behind you.
	''')

exits = {
	'up': 'src.story.undertown_entrance',
}

def buy(origin, *args):
	origin.write('You cannot buy anything, for you do not have any money.')
	return True, ''
