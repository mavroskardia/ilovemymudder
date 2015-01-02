import sys
import os
import inspect
import getpass
import importlib

try:
    import bcrypt
except ImportError:
    print('You must install the bcrypt package to continue. Try:\n\n\tpip install bcrypt')

from . import storage

from .server import Server

from ..common import config
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

def createuser(_username=None, _password=None, *args):
    username = _username or input('username: ')
    salt = bcrypt.gensalt()
    pw = _password or getpass.getpass('password: ')
    passwd_hash = bcrypt.hashpw(pw.encode(), salt)

    if not storage.store_user(username, salt, passwd_hash):
        print('\nFailed to store user. Please correct errors before trying again.')
        return 1

    user, session = storage.get_user(username)

    print('''
    Created user:
        {0.name} ({0.level} [{0.xp}])
        S: {0.strength} D: {0.dexterity} I: {0.intelligence} H: {0.health}
'''.format(user))

    return 0

def makerooms():
    print('Making rooms...')

    session = storage.get_session()
    storyfiles = ['src.story.'+f[:-3]
                    for f in os.listdir(config.storydir)
                    if not f.startswith('__') and f.endswith('.py')]

    for storyfile in storyfiles:
        print('\t', storyfile)
        storymodule = importlib.import_module(storyfile, package='src')
        if not hasattr(storymodule, 'is_start'): storymodule.is_start = False
        session.add(storage.Room(is_start=storymodule.is_start, module=storyfile))

    session.commit()

    print('done!')

def reset():
    os.remove(config.database_file)
    makerooms()
    createuser(_username='chryso', _password='letmein')
    runserver()

commandline_options = {
    'createuser': createuser,
    'runserver': runserver,
    'makerooms': makerooms,
    'reset': reset
}

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = commandline_options.get(sys.argv[1], usage)
        ret = command(*sys.argv[2:])
        sys.exit(ret)

    usage()
    sys.exit(1)
