is_start = True

name = "Town Square"

description = '''
        You are in the town square of the village of Harsden.  The village is
        built on one side of a small lake.  Draining into the lake is a creek
        that snakes its way through a dense forest that surrounds both the lake
        and village.

        Even though it is midday, no one is in the town square.  You do, 
        however, hear some commotion within the tavern nearby.'''

exits = {
    'north': 'src.story.tavern',
    'south': 'src.story.forest',
    'west': 'src.story.beach',    
}

