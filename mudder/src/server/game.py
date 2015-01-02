def build_status_string(status):
    statuses = []
    for s in UserStatus:
        if status & s.value:
            statuses.append(s.name)

    return ', '.join(statuses)

def build_exits_string(room):
    exits = room.exits
    num_exits = len(exits.keys())

    if num_exits == 0:
        return 'There is no way out!'

    # ret = 'There '
    # ret += 'are ' if num_exits > 1 else 'is '
    # ret += num_exits
    # ret += ' exits:\n' if num_exits > 1 else ' exit:\n'
    ret = '\n'.join(['To the {} is the {}.'.format(name, exits[name])
                        for name in exits])

    return ret
