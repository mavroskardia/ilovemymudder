import sys
import io
import datetime


class HijackedStdOut(io.TextIOWrapper):

    def write(self, s):
        if s == '\n':
            super().write(s)
            return
            
        now = datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S => ')
        s = '{}{}'.format(now, s)
        super().write(s)
        self.flush()


def hijack_stdout():
    sys.stdout = HijackedStdOut(buffer=sys.stdout.buffer)


if __name__ == '__main__':
    print('pre hijack')
    hijack_stdout()
    print('post hijack')
