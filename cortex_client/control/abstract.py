# control.abstract - Parent class for all controllers. Implements basic flow usage.
# coding: utf-8
#
# Copyright 2010 Guardis SPRL, Liège, Belgium.
# Authors: Laurent Eschenauer <laurent.eschenauer@guardis.com>
#
# This software cannot be used and/or distributed without prior
# authorization from Guardis.

from cortex_client.control.exceptions import ControllerException

class AbstractController(object):
    '''The default (abstract) controller'''

    def __init__(self):
        self._actions = {}
        self._default_action = lambda x : self._error("No default action defined", -1)

    def run(self, api, argv):
        '''Execute the action (first argument in argv with other arguments) from this controller'''
        self._api = api
        self._pre(argv)

        if len(argv) == 0:
            self._default_action(argv[1:])
        else:
            action = argv[0]
            if self._actions.has_key(action):
                self._actions[action](argv[1:])
            else:
                raise ControllerException("Pardon Monsieur ? I'm not sure I understand your request")

        self._post(argv)
        self._api = None

    def _pre(self, argv):
        pass

    def _post(self, argv):
        pass

    def _error(self, message, code=-1):
        print(message)
        exit(code)

    def _register(self, action, command):
        if isinstance(action, (list, tuple)):
            for a in action:
                self._actions[a] = command
        else:
            self._actions[a] = command

