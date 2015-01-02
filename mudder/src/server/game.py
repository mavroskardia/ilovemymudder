from .enums import UserStatus


def build_status_string(status):
    statuses = []
    for s in UserStatus:
        m = status & s.value
        if m != UserStatus.normal.value and m == s.value:
            statuses.append(s.name)

    if not statuses: statuses = ['feeling normal']

    return ', '.join(statuses)
