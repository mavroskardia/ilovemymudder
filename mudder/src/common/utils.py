import sys
import os
import shutil
import io
import datetime
import time
import importlib
import threading


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

class ModuleWatcher(object):

    watched_files = []

    def __init__(self, module, interval=5):
        self.module = module
        self.interval = interval
        self.thread = threading.Thread(target=self.loop)
        self.done = False
        if module.__file__ in ModuleWatcher.watched_files:
            raise Exception('This file is already being watched')
        ModuleWatcher.watched_files.append(module.__file__)

    def watch(self, action=None):
        self.action = action
        self.filename = self.module.__file__
        self.t0 = os.stat(self.filename).st_mtime
        self.thread.start()

    def loop(self):
        while not self.done:
            dt = os.stat(self.filename).st_mtime
            if dt != self.t0:
                print('{} was modified, reloading...'.format(self.module))
                importlib.reload(self.module)
                self.t0 = dt
                if self.action: self.action()
            time.sleep(self.interval)

    def stop(self):
        self.done = True
        self.thread.join()

def watch_and_reload(module):
    print('watching module {} for changes'.format(module))
    mw = ModuleWatcher(module)
    mw.watch()
    return mw

if __name__ == '__main__':

    if sys.argv[1] == 'clean':
        clean()
    elif sys.argv[1] == 'watch':
        mod = importlib.import_module('.test', package='src.common')
        watch = watch_and_reload(mod)

        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                watch.stop()
                break
