import pdb
import re
import sqlite3
import asyncio

from enum import Enum

from .storage import is_user_match
from ..common import config

class ServerState(Enum):
    Handshake = 1
    Authentication = 2
    Command = 3


class ServerProtocol(asyncio.Protocol):

    def __init__(self, server, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.server = server
        self.state = ServerState.Handshake

        self.protocol_actions = {
            ServerState.Handshake: self.handshake,
            ServerState.Authentication: self.authenticate,
            ServerState.Command: self.process_command,
        }

        self.commands = {
            'quit': self.server.quit,
            'say': self.server.say,
            'echo': self.echo,
        }

    def connection_made(self, transport):
        self.transport = transport
        self.server.connections.append(self)
        print('Accepted connection from {}'.format(transport.get_extra_info('peername')))

    def data_received(self, data):
        success, msg = self.protocol_actions.get(self.state, self.invalid_state)(data)
        if not success:
            print(msg)
            self.transport.close()

    def connection_lost(self, exc):
        if exc:
            print('Lost connection unexpectedly:', exc)

        print('connection closed')

    def handshake(self, data):
        msg = data.decode().strip()
        print('received "%s" as handshake (expecting "%s")' % (msg, config.version))
        if msg == config.version:
            self.transport.write(config.version.encode())
            self.state = ServerState.Authentication
            return True, 'accepted handshake'
        else:
            self.transport.write('NO\n'.encode())

        return False, 'handshake was not what we expected, closing'

    def authenticate(self, data):
        msg = data.decode().strip()
        print('attempting to authenticate against {}'.format(msg))

        pattern = r'^(\w+):(\w+)$'
        result = re.findall(pattern, msg)
        if not result:
            return False, 'not in username:password format (got %s, but expected %s)' % (msg, pattern)

        user, passwd = result[0]

        print('authenticating user "{}"'.format(user))

        if self.auth_user(user, passwd):
            self.state = ServerState.Command
            self.transport.write('OK'.encode())
            return True, 'successfully authenticated'

        self.transport.write('NO'.encode())
        return False, 'invalid user'

    def process_command(self, data):
        msg = data.decode().strip()
        pattern = r'\w+'
        command, *args = re.findall(pattern, msg)
        print('attempting to process command {} with args {}'.format(command, repr(args)))

        cmd = self.commands.get(command.lower(), self.invalid_command)
        if not args: args = []
        success, msg = cmd(*args)

        if not success:
            return False, msg

        return True, ''

    def invalid_state(self, data):
        return False, 'Failed to derive state "%s"' % self.state

    def invalid_command(self, *args):
        return False, 'Invalid command'

    def auth_user(self, user, passwd):
        return is_user_match(user, passwd)

    def echo(self, *args):
        msg = ' '.join([c.strip() for c in args if c])
        self.transport.write(msg.encode())
        return True, 'echoed "{}" to client'.format(msg)

    def close(self):
        self.transport.close()


class Server(object):

    def __init__(self):
        '''Make database connections (via SQLAlchemy?)'''
        self.loop = None
        self.server = None
        self.connections = []

    def quit(self, *args):
        # TODO: notify all clients, save state, etc.
        for c in self.connections:
            c.close()
        self.server.close()
        return True, 'quitting...'

    def say(self, *args):
        msg = ' '.join(args) + '\n'
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
