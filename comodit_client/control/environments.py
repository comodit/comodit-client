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
from comodit_client.control import completions
from comodit_client.control.groups import EnvironmentGroupsController
from comodit_client.control.exceptions import ArgumentException
from comodit_client.api.importer import Import
from comodit_client.control.doc import ActionDoc


class EnvironmentsController(OrganizationEntityController):

    _template = "environment.json"

    def __init__(self):
        super(EnvironmentsController, self).__init__()
        self._audit = AuditHelper(self, "<org_name> <res_name>")
        
        # subcontrollers
        self._register_subcontroller(["settings"], EnvironmentSettingsController())

        # actions
        self._register(["import"], self._import, self._print_import_completions)
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

        self._register_subcontroller(["groups"], EnvironmentGroupsController())
        self._register_action_doc(self._import_doc())

        self._doc = "Environments handling."

    def _get_collection(self, org_name):
        return self._client.environments(org_name)

    def _prune_json_update(self, json_wrapper):
        super(EnvironmentsController, self)._prune_json_update(json_wrapper)
        json_wrapper._del_field("settings")
        json_wrapper._del_field("hosts")
        json_wrapper._del_field("organization")

    def _import(self, argv):
        """
        Pushes local data to comodit server. Data may include applications,
        distributions, platforms, organizations, environments and hosts.
        Local data are automatically imported if no collision with remote data
        is detected. In case of collision, 'force' option can be used to still
        import data.
        """
        self._options = self._config.options
        org = self._client.organizations().get(argv[0])

        if len(argv) < 2:
            raise ArgumentException("Wrong number of arguments")

        importer = Import(self._config.options.skip_conflict, queue_actions=True,
                          with_instances=self._config.options.with_instances)
        importer.import_full_env(org, argv[1])

        if  self._config.options.dry_run:
            importer.display_queue(show_only_conflicts = False)
        elif (importer.no_conflict() or self._config.options.skip_conflict):
            importer.execute_queue()
        else:
            importer.display_queue(show_only_conflicts = True)
            print ("Impossible to import environment. There are conflicts. Use --skip-conflict to force")


    def _print_import_completions(self, param_num, argv):
        if param_num < 1:
            self._print_entity_completions(param_num, argv)
        elif param_num == 1:
            completions.print_dir_completions()

    def _import_doc(self):
        return ActionDoc("import", "<src_folder> [--dry-run]", """
            Import environment from disk. With --dry-run, actions are displayed but not applied.""")
