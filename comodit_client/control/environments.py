# control.environments - Controller for comodit Environments entities.
# coding: utf-8
#
# Copyright 2010 Guardis SPRL, Liège, Belgium.
# Authors: Laurent Eschenauer <laurent.eschenauer@guardis.com>
#
# This software cannot be used and/or distributed without prior
# authorization from Guardis.

from comodit_client.control.organization_entity import OrganizationEntityController
from comodit_client.control.settings import EnvironmentSettingsController
from comodit_client.control.audit import AuditHelper
from comodit_client.control.notification_log import NotificationLogHelper
from comodit_client.control.log import OtherLogHelper
from comodit_client.control.log import AgentLogHelper

class EnvironmentsController(OrganizationEntityController):

    _template = "environment.json"

    def __init__(self):
        super(EnvironmentsController, self).__init__()
        self._audit = AuditHelper(self, "<org_name> <res_name>")
        
        # subcontrollers
        self._register_subcontroller(["settings"], EnvironmentSettingsController())

        # actions
        self._register(["audit-logs"], self._audit.audit, self._print_entity_completions)
        self._register_action_doc(self._audit.audit_doc())
        
        self._notificationLog = NotificationLogHelper(self, "<org_name> <res_name>")
        self._register(["notification-logs"], self._notificationLog.notification_log, self._print_entity_completions)
        self._register_action_doc(self._notificationLog.notification_log_doc())
        
        self._agentLog = AgentLogHelper(self, "<org_name> <res_name>")
        self._register(["agent-logs"], self._agentLog.agent_log, self._print_entity_completions)
        self._register_action_doc(self._agentLog.agent_log_doc())
        
        self._otherLog = OtherLogHelper(self, "<org_name> <res_name>")
        self._register(["other-logs"], self._otherLog.other_log, self._print_entity_completions)
        self._register_action_doc(self._otherLog.other_log_doc())
        

        self._doc = "Environments handling."

    def _get_collection(self, org_name):
        return self._client.environments(org_name)

    def _prune_json_update(self, json_wrapper):
        super(EnvironmentsController, self)._prune_json_update(json_wrapper)
        json_wrapper._del_field("settings")
        json_wrapper._del_field("hosts")
        json_wrapper._del_field("organization")
