import random


name = 'Dragon\'s Tooth Fight Club'

description = '''
	You descend the stairs and see the village's makeshift arena in action.

	There are two men beating each other to a bloody pulp.

	There is an organizer waiting for the next contestant.'''


exits = {
	'upstairs': 'src.story.tavern',
}


def fight(origin):
	msg = '''
	A burly looking dude enters the ring from the other side.
	
	The match begins suddenly as he lunges for you!
	'''

	origin.write(msg)

	fighting = True
	choices = (True, False)

	while fighting:
		you = random.choice(choices)
		him = random.choice(choices)

		youdmg = random.randint(1,10)
		himdmg = random.randint(1,10)



