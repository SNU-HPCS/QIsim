#!/usr/bin/python3

import sys, os, io
from subprocess import Popen, run, PIPE, STDOUT, DEVNULL

__all__ = ['cacti_interface_pb2']

def get_cacti_dir():
    return os.path.dirname(os.path.realpath(__file__))

def get_cacti_path(reproduce=False):
    if not reproduce:
        return os.path.join(get_cacti_dir(), "cacti")
    else:
        return os.path.join(get_cacti_dir(), "cacti_reproduce")

def cacti(argv=None, proto=None, reproduce=False, print_stderr=False, valgrind=False):
    cacti_command = [get_cacti_path(reproduce)]

    if proto:
        cacti_command.append("-proto")

    if argv:
        cacti_command += argv

    if valgrind:
        print_stderr = True
        cacti_command = ['valgrind'] + cacti_command + ['--track-origins=yes']

    if print_stderr:
        stderr_val = STDOUT
    else:
        stderr_val = DEVNULL

    if proto:
        cacti = Popen(cacti_command, stdin=PIPE, stdout=PIPE, stderr=stderr_val, cwd=get_cacti_dir())
        cacti_output, _ = cacti.communicate(proto.SerializeToString())
        return cacti_output.decode('utf-8')
    else:
        return run(cacti_command, stdin=DEVNULL, stdout=PIPE, stderr=stderr_val, cwd=get_cacti_dir(), universal_newlines=True)

def main():
    for line in cacti(sys.argv[1:]):
        print(line.strip('\n'))

if __name__ == '__main__':
    main()
