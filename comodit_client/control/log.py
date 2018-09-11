# coding: utf-8

from __future__ import print_function
from builtins import object
from comodit_client.control.doc import ActionDoc

class AgentLogHelper(object):
    def __init__(self, ctrl, agent_log_params):
        self._ctrl = ctrl
        self._params = agent_log_params

    def agent_log(self, argv):
        res = self._ctrl._get_entity(argv)
        logs = res.agent_logs().list()

        # Display the result
        for log in logs:
            print(log.timestamp, log.message)

    def agent_log_doc(self):
        return ActionDoc("agent log", self._params, """
        Displays agent log.""")

class OtherLogHelper(object):
    def __init__(self, ctrl, other_log_params):
        self._ctrl = ctrl
        self._params = other_log_params

    def other_log(self, argv):
        res = self._ctrl._get_entity(argv)
        logs = res.other_logs().list()

        # Display the result
        for log in logs:
            print(log.timestamp, log.message)

    def other_log_doc(self):
        return ActionDoc("other log", self._params, """
        Displays other log.""")

