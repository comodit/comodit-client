# coding: utf-8

from __future__ import print_function
from builtins import object
from comodit_client.control.doc import ActionDoc

class NotificationLogHelper(object):
    def __init__(self, ctrl, notification_log_params):
        self._ctrl = ctrl
        self._params = notification_log_params

    def notification_log(self, argv):
        res = self._ctrl._get_entity(argv)
        logs = res.notification_logs().list()

        # Display the result
        for log in logs:
            print(log.timestamp, log.message)

    def notification_log_doc(self):
        return ActionDoc("notification log", self._params, """
        Displays notification log.""")
