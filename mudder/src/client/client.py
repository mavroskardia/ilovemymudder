import time
import asyncio
import getpass

from enum import Enum

try:
    from socket import socketpair
except ImportError:
    from asyncio.windows_utils import socketpair

from ..common import config


class ClientState(Enum):
    Initial = 1
    Handshake = 2
    Authentication = 3
    Command = 4


class ClientProtocol(asyncio.Protocol):

    def __init__(self, client, username, passwd, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.username = username
        self.passwd = passwd  # should probably send over SSL if I keep going
        self.client = client
        self.state = ClientState.Initial
        self.client_actions = {
            ClientState.Handshake: self.receive_handshake,
            ClientState.Authentication: self.receive_auth,
            ClientState.Command: self.receive_command_result,
        }
        self.commands = {
            'echo': lambda *args: self.send('echo ' + (' '.join(args))),
            'quit': lambda: self.send('quit'),
            'say': lambda *args: self.send('say ' + (' '.join(args))),
        }

    def connection_made(self, transport):
        self.transport = transport
        self.send_handshake()

    def data_received(self, data):
        result = self.client_actions.get(self.state, self.unimplemented_action)(data)

    def connection_lost(self, exc):
        print('connection lost')
        self.client.loop.stop()

    def send(self, msg):
        self.transport.write(msg.encode())

    def send_handshake(self):
        self.transport.write(config.version.encode())
        self.state = ClientState.Handshake

    def receive_handshake(self, data):
        msg = data.decode().strip()
        if msg != config.version:
            print('got the wrong handshake, quitting')
            self.transport.close()

        s = '{}:{}'.format(self.username, self.passwd)
        self.transport.write(s.encode())
        self.state = ClientState.Authentication

    def receive_auth(self, data):
        msg = data.decode().strip()
        if msg == 'NO':
            print('failed to authenticate, quitting')
            self.transport.close()
        elif msg == 'OK':
            print('authenticated successfully, beginning command loop')
            self.state = ClientState.Command
            self.process_next_command()

    def receive_command_result(self, data):        
        print(data.decode().strip())
        self.process_next_command()

    def unimplemented_action(self, data):
        print('client tried to execute an unimplemented state "{}"'.format(self.state))

    def process_next_command(self):
        valid = False
        while not valid:
            cmd = input('=> ')
            cmd, *args = [c.strip() for c in cmd.split(' ') if c]
            valid = cmd in self.commands
            if not valid:
                self.invalid_command()

        self.commands.get(cmd, self.invalid_command)(*args)

    def invalid_command(self, *args):
        print('That is not a command. Type "help" for possible commands.')
        self.process_next_command()


class Client(object):

    def run(self):
        self.main_loop(*self.get_userinfo())

    def get_userinfo(self):
        return input('username > '), getpass.getpass('password > ')

    def main_loop(self, username, passwd):
        self.rsock, self.wsock = socketpair()
        self.loop = asyncio.get_event_loop()

        coro = self.loop.create_connection(lambda: ClientProtocol(self, username, passwd), config.host, config.port)

        self.loop.run_until_complete(coro)
        self.loop.run_forever()
        self.loop.close()
