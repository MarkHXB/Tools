import time
from termcolor import cprint
import os
from datetime import datetime


class File():
    def __init__(self, path):
        self.path = path
        self.c_time = os.path.getctime(self.path)
        self.m_time = os.path.getmtime(self.path)
        self.is_alive = self.file_is_alive()

    def file_is_alive(self):
        if os.path.exists(self.path):
            return True
        return False

    def is_created():
        pass

    def is_modified():
        pass

    def is_deleted():
        pass


class Observer():
    def __init__(self, path, delay, log_file):
        self.path = path
        self.delay = delay
        self.log_file = log_file
        self.pre_values = []
        self.after_values = []
        self.init()

    def init(self):
        self.file_is_alive()

    def file_is_alive(self):
        if os.path.exists(self.path):
            return True
        return False

    def scan(self):
        if os.path.isfile(r'{}'.format(self.path)):
            return File(path=r'{}'.format(self.path))
        else:
            files = []
            self.path = self.path.replace('"', '')
            for r, d, f in os.walk(self.path):
                try:
                    for directory in d:
                        d_path = os.path.join(r, directory)
                        dir = File(path=d_path)
                        files.append(dir)
                    for file in f:
                        t_path = os.path.join(r, file)
                        c_file = File(path=t_path)
                        files.append(c_file)
                except IOError as e:
                    cprint(f'[ NOT ALLOWED TO READ ] {r}', color="magenta")
                except Exception as e:
                    cprint(
                        f'[ INTERNAL ERROR ] when reading {r}', color="cyan")

            return files

    def scan_privileges(self):
        return os.access(self.path, os.R_OK)

    def compare(self, seconds):
        if self.log_file == '' or self.log_file == None:
            for file in self.after_values:
                if seconds < file.c_time:
                    cprint(f'[ CREATED ] {file.path}', color="green")
                elif seconds < file.m_time:
                    cprint(f'[ MODIFIED ] {file.path}', color='yellow')

            p_paths = [file.path for file in self.pre_values]
            a_paths = [file.path for file in self.after_values]

            deleted = list(set(p_paths) - set(a_paths))

            if deleted:
                for file in deleted:
                    cprint(f'[ DELETED ] {file}', color="red")

        else:
            changes = []
            for file in self.after_values:
                if seconds < file.c_time:
                    changes.append(f'[ CREATED ] {file.path}')
                elif seconds < file.m_time:
                    changes.append(f'[ MODIFIED ] {file.path}')

            p_paths = [file.path for file in self.pre_values]
            a_paths = [file.path for file in self.after_values]

            deleted = list(set(p_paths) - set(a_paths))

            if deleted:
                for file in deleted:
                    changes.append(f'[ DELETED ] {file}')
            
            if changes:
                with open(rf'{self.log_file}', 'a') as f:
                    for line in changes:
                        f.write("%s \n" % line)

    def run(self):
        # first initialize scan to prepare pre_values
        start_time = time.time()
        have_enough_priv = self.scan_privileges()
        if have_enough_priv:
            while True:
                self.pre_values = self.scan()

                dt = datetime.today()
                seconds = dt.timestamp()

                time.sleep(self.delay)

                self.after_values = self.scan()

                self.compare(seconds)
        else:
            cprint(f'[ NOT ALLOWED TO READ ] {self.path}', color="magenta")


def usage():
    print('Szia')


if __name__ == '__main__':
    import getopt
    import sys
    msg = ''

    path = ''
    delay = 0.0
    log_file = ''

    try:
        opts, arg = getopt.getopt(sys.argv[1:], 'path:delay:log', [
                                  'path=', 'delay=', 'log=', 'help'])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit(2)
        elif opt in ('-p', '--path'):
            path = arg
        elif opt in ('-d', '--delay'):
            delay = arg
            delay = float(delay)
        elif opt in ('-l', '--log'):
            log_file = arg
        else:
            usage()
            sys.exit(2)

    if (path == '' or path == None) or (delay == 0.0 or delay == None):
        usage()
        sys.exit(2)

    print(log_file)
    observer = Observer(path=path, delay=delay, log_file=log_file)
    observer.run()
