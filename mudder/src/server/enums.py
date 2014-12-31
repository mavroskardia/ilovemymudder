from enum import Enum


class UserStatus(Enum):
    normal = 0
    wet = 1
    injured = 2


class ServerState(Enum):
    Handshake = 1
    Authentication = 2
    Command = 3
