import sys
import getpass
try:
    import bcrypt
except ImportError:
    print('You must install the bcrypt package to continue. Try:\n\n\tpip install bcrypt')

from .server import Server
from .storage import store_user, get_user
from ..common.utils import hijack_stdout

def usage(*args):
    print('''
usage: {} [command] [options]

    Where available commands are:

        runserver       Runs the game server forever
        createuser      Creates a new player for the game
'''.format(sys.argv[0]))

def runserver(*args):
    hijack_stdout()
    Server().run()
    return 0

def createuser(*args):
    username = input('username: ')
    salt = bcrypt.gensalt()
    passwd_hash = bcrypt.hashpw(getpass.getpass('password: ').encode(), salt)
    store_user(username, salt, passwd_hash)
    user = get_user(username)
    print('''
    Created user:
        {}
        S: {} D: {} I: {} H: {}
'''.format(user.name, user.strength, user.dexterity,
            user.intelligence, user.health))
            
    return 0

commandline_options = {
    'createuser': createuser,
    'runserver': runserver
}

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = commandline_options.get(sys.argv[1], usage)
        ret = command(*sys.argv[2:])
        sys.exit(ret)

    usage()
    sys.exit(1)
