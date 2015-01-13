import random


name = 'Dragon\'s Tooth Fight Club'

description = '''
	You descend the stairs and see the village's makeshift arena in action.

	There are two men beating each other to a bloody pulp.

	There is an organizer waiting for the next contestant.'''


exits = {
	'upstairs': 'src.story.tavern',
}


def fight(origin, *args):
	msg = '''
	A burly looking dude enters the ring from the other side.

	The match begins suddenly as he lunges for you!
	'''

	fighting = True
	choices = (True, False)

	himhealth = 10

	while fighting:
		you = random.choice(choices)
		him = random.choice(choices)

		youdmg = random.randint(1,10) * origin.user.strength
		himdmg = random.randint(1,5)

		himhealth -= youdmg

		msg += '''
	He hits you for {}.
	You hit him for {}.
	He has {} health left.'''.format(himdmg, youdmg, himhealth)

		if himhealth <= 0:
			msg += '\n\n\tHe\'s dead.\n'
			fighting = False
			origin.write(msg)
			origin.add_xp('beating him to a pulp', 470)
		else:
			origin.write(msg)

		origin.add_hp(-himdmg)

	return True, ''
