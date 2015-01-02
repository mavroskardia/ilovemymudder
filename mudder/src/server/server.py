import pdb
import re
import sqlite3
import asyncio
import importlib
import threading
import time

from . import game, storage
from .enums import UserStatus, ServerState
from ..common import config, utils

class ServerProtocol(asyncio.Protocol):

    def __init__(self, server, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.server = server
        self.state = ServerState.Handshake
        self.user = None
        self.session = None

        self.protocol_actions = {
            ServerState.Handshake: self.handshake,
            ServerState.Authentication: self.authenticate,
            ServerState.Command: self.process_command,
        }

        self.commands = {
            'quit': self.server.quit,
            'say': lambda *args: self.server.say(self, *args),
            'echo': self.echo,
            'disconnect': self.close,
            'stats': lambda *args: self.server.stats(self, *args),
            'look': lambda: self.server.look(self),
        }

    def connection_made(self, transport):
        self.transport = transport
        self.server.connections.append(self)
        print('Accepted connection from {}'.format(transport.get_extra_info('peername')))

    def data_received(self, data):

        success, msg = self.protocol_actions.get(self.state, self.invalid_state)(data)
        if not success:
            print('Client sent invalid command ("{}")'.format(data.decode()))
            self.write(msg)

    def connection_lost(self, exc):
        if exc:
            print('Lost connection unexpectedly:', exc)

        print('connection closed')

    def write(self, msg):
        self.transport.write(msg.encode())

    def handshake(self, data):
        msg = data.decode()
        print('received "%s" as handshake (expecting "%s")' % (msg, config.version))
        if msg == config.version:
            self.write(config.version)
            self.state = ServerState.Authentication
            return True, 'accepted handshake'
        else:
            self.write('NO\n')

        return False, 'handshake was not what we expected, closing'

    def authenticate(self, data):
        msg = data.decode().strip()

        pattern = r'^(\w+):(\w+)$'
        result = re.findall(pattern, msg)
        if not result:
            self.write('NO')            
            return False, ''#'not in username:password format (got %s, but expected %s)' % (msg, pattern)

        user, passwd = result[0]

        print('authenticating user "{}"'.format(user))

        if self.auth_user(user, passwd):
            self.state = ServerState.Command
            self.write('OK')
            self.user, self.session = storage.get_user(user)
            return True, 'successfully authenticated'

        self.write('NO')
        return False, 'invalid user'

    def process_command(self, data):
        msg = data.decode().strip()
        pattern = r'[!-~]+'
        command, *args = re.findall(pattern, msg)
        print('attempting to process command {} with args {}'.format(command, repr(args)))

        cmd = self.commands.get(command.lower(), lambda *args: self.server.room_command(self, command, *args))
        if not args: args = []
        success, msg = cmd(*args)

        if not success:
            return False, msg

        return True, ''

    def invalid_state(self, data):
        return False, 'Failed to derive state "%s"' % self.state

    def invalid_command(self, *args):
        return False, 'Unknown command'

    def auth_user(self, user, passwd):
        return storage.is_user_match(user, passwd)

    def echo(self, *args):
        msg = ' '.join([c.strip() for c in args if c])
        self.write(msg)
        return True, 'echoed "{}" to client'.format(msg)

    def close(self):
        self.transport.close()

    def set_status(self, status, value):
        mask = 1 << status.value
        self.user.status &= ~mask

        if value:
            self.user.status |= mask

    def call_after(self, seconds, callback):
        def f():
            time.sleep(seconds)
            callback()
        t = threading.Thread(target=f)
        t.start()


class Server(object):

    def __init__(self):
        self.loop = None
        self.server = None
        self.connections = []
        self.room_modules = {}

    def quit(self, *args):
        # TODO: notify all clients, save state, etc.
        for c in self.connections:
            c.close()
        self.server.close()
        return True, 'quitting...'

    def say(self, origin, *args):
        msg = '\n'
        msg += '{}: '.format(origin.user.name)
        msg += ' '.join(args)
        msg += '\n'

        for c in self.connections:
            c.transport.write(msg.encode())

        return True, 'sent %s to all connections' % msg

    def run(self):
        print('Started server listening at {}:{}\n'.format(config.host, config.port))

        self.loop = asyncio.get_event_loop()
        self.server = self.loop.run_until_complete(self.loop.create_server(lambda: ServerProtocol(self),
                                                                        config.host, config.port))

        try:
            self.loop.run_until_complete(self.server.wait_closed())
        except KeyboardInterrupt:
            print('Caught Ctrl-C, quitting')
            self.quit()

    def stats(self, origin, *args):
        user = origin.user
        status = 'You are {}.'.format(game.build_status_string(user.status))
        msg = '''
        {0.name} Level {0.level} XP: {0.xp}
            Health:         {0.health}
            Strength:       {0.strength}
            Dexterity:      {0.dexterity}
            Intelligence:   {0.intelligence}

            Status: {1}
'''

        origin.transport.write(msg.format(user, status).encode())

        return True, ''

    def look(self, origin, *args):
        user = origin.user
        dashes = '-' * len(user.current_room.name)
        room = self.cache_room_module(user.current_room)
        exits = game.build_exits_string(room)
        msg = '\n{0.name}\n\t{1}\n\t{0.description}\n\t{2}'
        origin.transport.write(msg.format(user.current_room, dashes, exits).encode())
        return True, ''

    def room_command(self, origin, cmd, *args):
        if not origin.user.current_room.commands_file:
            return False, 'No room commands in this room'

        room_module = self.cache_room_module(origin.user.current_room)

        if not room_module:
            return False, 'Could not find room module'

        if not hasattr(room_module, cmd):
            print('Room module exists, but command "{}" does not.'.format(cmd))
            return False, 'Could not find this particular command'

        cmdexec = getattr(room_module, cmd)
        cmdexec(origin, *args)

        return True, ''

    def cache_room_module(self, room):
        assert room is not None

        if room.id in self.room_modules:
            return self.room_modules[room.id]

        try:
            self.room_modules[room.id] = importlib.import_module(room.commands_file, package='src')
        except ImportError as e:
            print('Failed to import room: {}'.format(e))
            return None

        return self.room_modules.get(room.id, None)
