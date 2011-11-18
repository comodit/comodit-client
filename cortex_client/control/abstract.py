# control.abstract - Parent class for all controllers. Implements basic flow usage.
# coding: utf-8
#
# Copyright 2010 Guardis SPRL, Liège, Belgium.
# Authors: Laurent Eschenauer <laurent.eschenauer@guardis.com>
#
# This software cannot be used and/or distributed without prior
# authorization from Guardis.

import sys

from cortex_client.util import globals
from cortex_client.control.exceptions import ControllerException

class AbstractController(object):
    '''The default (abstract) controller'''

    def __init__(self):
        self._actions = {}
        self._completions = {}
        self._register("__available_actions", self._available_actions)
        self._default_action = lambda x : self._error("No default action defined", -1)

    def run(self, api, argv):
        '''Execute the action (first argument in argv with other arguments) from this controller'''
        self._api = api
        self._pre(argv)

        if len(argv) == 0:
            self._default_action(argv[1:])
        else:
            action = argv[0]
            if globals.options.param_completions >= 0:
                if self._completions.has_key(action):
                    self._completions[action](globals.options.param_completions, argv[1:])
                return

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

    def _error(self, message, code = -1):
        print(message)
        exit(code)

    def _register(self, action, command, print_complete = None):
        if isinstance(action, (list, tuple)):
            for a in action:
                self._actions[a] = command
                if print_complete:
                    self._completions[a] = print_complete
        else:
            self._actions[action] = command
            if print_complete:
                    self._completions[action] = print_complete

    def _available_actions(self, argv):
        for k in self._actions.keys():
            if k[0] != '_':
                print k

    def _print_escaped_name(self, name):
        if name is None:
            return
        name = name.replace("\\", "\\\\")
        name = name.replace(" ", "\\ ")
        print name.decode("utf-8")

    def _equals_identifiers(self, id1, id2):
        if id1 is None or id2 is None:
            return False

        u_id1 = id1
        if isinstance(id1, basestring):
            u_id1 = id1.decode("utf-8")
        u_id2 = id2
        if isinstance(id2, basestring):
            u_id2 = id2.decode("utf-8")

        return u_id1 == u_id2

    def _print_resource_identifiers(self, res_list, current_id = None):
        for r in res_list:
            self._print_escaped_name(r.get_identifier())
