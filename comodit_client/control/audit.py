# coding: utf-8

from __future__ import print_function
from builtins import object
from comodit_client.control.doc import ActionDoc

class AuditHelper(object):
    def __init__(self, ctrl, audit_params):
        self._ctrl = ctrl
        self._params = audit_params

    def audit(self, argv):
        res = self._ctrl._get_entity(argv)
        logs = res.audit_logs().list()

        # Display the result
        for log in logs:
            user = log.user_full_name
            if user is None or user == "":
                user = log.username
            print(log.timestamp, log.message, "by", user)

    def audit_doc(self):
        return ActionDoc("audit", self._params, """
        Displays audit log.""")
