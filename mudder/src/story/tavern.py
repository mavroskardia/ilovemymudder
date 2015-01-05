from ..common import storyutils
from ..server.enums import UserStatus

drinks = 0

name = "Dragon's Tooth Tavern"

description = '''
	The tavern is loud and boisterous.  On the far wall is a long bar 
	with two bartenders helping regulars.  To your left there are tables
	full of patrons drinking and talking amongst themselves.  To your 
	right, there is a crowd leaning as one over a solid wood railing, 
	cheering into the room below.'''

exits = {
	'south': 'src.story.town_center',
	'downstairs': 'src.story.fight_club',
}

def order(origin, *args):
	obj = storyutils.remove_articles(args)
	gosouth = False
	msg = 'You order a {} from the bartender'.format(obj)
	hploss = 0
	xpgain = 0

	if origin.has_status(UserStatus.drunk):
		hploss = -5
		xpgain = 217
		msg += '''...
	But you are too drunk to hit your mouth.  The liquor whizzes past your head
	and splashes onto the floor.  It's ok though, because you involuntarily
	follow it headfirst.  

	Your skull cracks hard against the wood floor.  You awaken back in the
	town square.'''

		origin.set_status(UserStatus.drinking, False)
		origin.set_status(UserStatus.buzzing, False)
		origin.set_status(UserStatus.drunk, False)		
		gosouth = True

	elif origin.has_status(UserStatus.buzzing):
		msg += '.  You are wasted.'	
		origin.set_status(UserStatus.drunk, True)
		origin.set_status(UserStatus.drinking, False)
		origin.set_status(UserStatus.buzzing, False)
	
	elif origin.has_status(UserStatus.drinking):
		msg += '. Still delicious.'
		origin.set_status(UserStatus.buzzing, True)
		origin.set_status(UserStatus.drinking, False)
	
	else:	
		msg += ' and slam it down.'
		origin.set_status(UserStatus.drinking, True)
		origin.set_status(UserStatus.buzzing, False)
		origin.set_status(UserStatus.drunk, False)

	origin.write(msg)
	
	if gosouth and origin.user.health > 0:
		origin.process_command('go south'.encode())

	if hploss:
		origin.add_hp(hploss)
		
	if xpgain:
		origin.add_xp('getting drunk', xpgain)
		
	
	return True, ''


drink = order