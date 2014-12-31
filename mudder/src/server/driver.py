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

def createuser(*args):
    username = input('username: ')
    salt = bcrypt.gensalt()
    passwd_hash = bcrypt.hashpw(getpass.getpass('password: ').encode(), salt)

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
    print('Making rooms...', end='')

    session = storage.get_session()
    storyfiles = ['src.story.'+f[:-3]
                    for f in os.listdir(config.storydir)
                    if not f.startswith('__') and f.endswith('.py')]

    for storyfile in storyfiles:
        print('loading story piece', storyfile)
        storymodule = importlib.import_module(storyfile, package='src')
        room = storage.Room()
        room.name = storymodule.name
        room.description = storymodule.description
        room.is_start = storymodule.is_start
        room.commands_file = storyfile
        session.add(room)

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
