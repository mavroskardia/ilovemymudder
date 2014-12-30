import time
import asyncio
import getpass
import threading

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

        self.interpreter = Interpreter(self)

    def connection_made(self, transport):
        self.transport = transport
        self.send_handshake()

    def data_received(self, data):
        result = self.client_actions.get(self.state, self.unimplemented_action)(data)

    def connection_lost(self, exc):
        print('connection lost')
        self.interpreter_done = True
        self.interpreter.stop()
        self.client.loop.stop()

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
            self.interpreter.start()

    def receive_command_result(self, data):
        print(data.decode().strip())

    def unimplemented_action(self, data):
        print('client tried to execute an unimplemented state "{}"'.format(self.state))


class Interpreter(object):

    def __init__(self, client_protocol):
        self.protocol = client_protocol
        self.commands = {
            'echo': lambda *args: self.send('echo ' + (' '.join(args))),
            'serverquit': lambda: self.send('quit'),
            'quit': lambda: self.stop,
            'say': lambda *args: self.send('say ' + (' '.join(args))),
            'help': self.help
        }

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def stop(self):
        self.running = False
        self.protocol.transport.close()

    def send(self, msg):
        self.protocol.transport.write(msg.encode())

    def run(self):
        while self.running:
            cmd = input('=> ')
            if not cmd:
                continue
            cmd, *args = [c.strip() for c in cmd.split(' ') if c]
            valid = cmd in self.commands
            if not valid:
                print('That is not a command. Type "help" for possible commands.')

            self.commands.get(cmd, lambda: self.help('{} is not a valid command.'.format(cmd)))(*args)

    def help(self, msg=None):
        commands = '\n\t' + '\n\t'.join(self.commands.keys())
        if msg:
            print(msg)
        print(commands)

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
