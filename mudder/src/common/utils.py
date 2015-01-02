import sys
import os
import shutil
import io
import datetime


class HijackedStdOut(io.TextIOWrapper):

    def write(self, s):
        if s == '\n':
            super().write(s)
            return

        s = '{:%Y.%m.%d %H:%M:%S} => {}'.format(datetime.datetime.now(), s)
        super().write(s)
        self.flush()


def hijack_stdout():
    sys.stdout = HijackedStdOut(buffer=sys.stdout.buffer)

def clean():
    dirs_to_remove = []
    for path, dirs, files in os.walk(os.curdir):
        if path.endswith('__pycache__'):
            dirs_to_remove.append(path)

    for d in dirs_to_remove:
        print('cleaning', d)
        shutil.rmtree(d)

if __name__ == '__main__':
    clean()
