# coding: utf-8

from __future__ import print_function
from __future__ import absolute_import
from builtins import str
from builtins import input
from builtins import object
import sys, readline

from comodit_client.api import Client
from comodit_client.console.utils import merge_escaped
from .commands import Commands


class ComodITConsole(object):
    def __init__(self, debug = False):
        self._cmds = None
        self._debug = debug

    def interact(self):
        if self._cmds == None:
            raise Exception("Console must be connected")

        readline.parse_and_bind('tab: complete')
        readline.set_completer_delims(readline.get_completer_delims().replace('-', ''))

        while True:
            try:
                readline.set_completer(self._cmds.get_completer())
                line = input(self._cmds.prompt() + "> ")
                self.execute_line(line)
            except EOFError:
                print()
                break
            except KeyboardInterrupt:
                print()  # skip a line
                continue

    def execute_file(self, path):
        with open(path, 'r') as f:
            for line in f:
                self.execute_line(line)

    def connect(self, api_url, username, password, insecure = False, mfa = None):
        self._cmds = Commands(Client(api_url, username, password, insecure, mfa))
        self._cmds.set_debug(self._debug)

    def execute_line(self, line):
        # Strip comments out
        index = line.find('#')
        if index >= 0:
            line = line[0:index]
        line = line.strip()
        # If line is empty, do nothing
        if line != '':
            args = merge_escaped(line.split())
            self._execute(args)

    def _execute(self, args):
        if len(args) == 0:
            # Nothing to do
            return

        try:
            self._cmds.call(args)
        except Exception as e:
            sys.stderr.write(str(e) + "\n")
            if self._debug:
                sys.exit(1)
