from enum import Enum


class UserStatus(Enum):
    normal 			= 0
    wet				= 1
    injured			= 2
    drinking 		= 4
    buzzing			= 8
    drunk 			= 16


class ServerState(Enum):
    Handshake = 1
    Authentication = 2
    Command = 3
