import sys
import getpass
try:
    import bcrypt
except ImportError:
    print('You must install the bcrypt package to continue. Try:\n\n\tpip install bcrypt')

from .server import Server
from . import storage
from ..common.utils import hijack_stdout

def usage(*args):
    print('''
usage: {} [command] [options]

    Where available commands are:

        runserver       Runs the game server forever
        createuser      Creates a new player for the game
        makerooms       Builds the rooms into the database
'''.format(sys.argv[0]))

def runserver(*args):
    hijack_stdout()
    Server().run()
    return 0

def createuser(*args):
    username = input('username: ')
    salt = bcrypt.gensalt()
    passwd_hash = bcrypt.hashpw(getpass.getpass('password: ').encode(), salt)

    if not storage.store_user(username, salt, passwd_hash):
        print('\nFailed to store user. Please correct errors before trying again.')
        return 1

    user = storage.get_user(username)

    print('''
    Created user:
        {} ({} [{}])
        S: {} D: {} I: {} H: {}
'''.format(user.name, user.level, user.xp, user.strength, user.dexterity,
            user.intelligence, user.health))

    return 0

def makerooms():
    print('Making rooms...', end='')
    session = storage.get_session()
    starting_room = storage.Room(name="Town Square", is_start=True,
        description='This is the town\'s square. Nothing is going on.',
        commands_file='story.town_center')
    session.add(starting_room)
    session.commit()
    print('done!')

commandline_options = {
    'createuser': createuser,
    'runserver': runserver,
    'makerooms': makerooms
}

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = commandline_options.get(sys.argv[1], usage)
        ret = command(*sys.argv[2:])
        sys.exit(ret)

    usage()
    sys.exit(1)
