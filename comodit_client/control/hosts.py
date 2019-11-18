# control.hosts - Controller for comodit Hosts entities.
# coding: utf-8
#
# Copyright 2010 Guardis SPRL, Liège, Belgium.
# Authors: Laurent Eschenauer <laurent.eschenauer@guardis.com>
#
# This software cannot be used and/or distributed without prior
# authorization from Guardis.

import subprocess

from comodit_client.config import Config
from comodit_client.control import completions
from comodit_client.control.alerts import MonitoringAlertController
from comodit_client.control.audit import AuditHelper
from comodit_client.control.changes import ChangeController
from comodit_client.control.compliance import ComplianceController
from comodit_client.control.contexts import PlatformContextController, \
    DistributionContextController, ApplicationContextController
from comodit_client.control.entity import EntityController
from comodit_client.control.exceptions import ArgumentException, MissingException, \
    ControllerException
from comodit_client.control.instances import InstancesController
from comodit_client.control.settings import HostSettingsController
from comodit_client.control.tree_rendering import TreeRenderer
from comodit_client.control.groups import HostGroupsController
from comodit_client.util import prompt
from comodit_client.control.notification_log import NotificationLogHelper
from comodit_client.control.log import OtherLogHelper
from comodit_client.control.log import AgentLogHelper
from comodit_client.control.actions import ActionController
from comodit_client.api.importer import Import
from comodit_client.control.doc import ActionDoc

class HostsController(EntityController):

    _template = "host.json"

    def __init__(self):
        super(HostsController, self).__init__()
        self._audit = AuditHelper(self, "<org_name> <env_name> <res_name>")
        self._notificationLog = NotificationLogHelper(self, "<org_name> <env_name> <res_name>")
        self._agentLog = AgentLogHelper(self, "<org_name> <env_name> <res_name>")
        self._otherLog = OtherLogHelper(self, "<org_name> <env_name> <res_name>")
        
        # subcontrollers
        self._register_subcontroller(["settings"], HostSettingsController())
        self._register_subcontroller(["instance"], InstancesController())
        self._register_subcontroller(["applications"], ApplicationContextController())
        self._register_subcontroller(["distribution"], DistributionContextController())
        self._register_subcontroller(["platform"], PlatformContextController())
        self._register_subcontroller(["compliance"], ComplianceController())
        self._register_subcontroller(["changes"], ChangeController())
        self._register_subcontroller(["alerts"], MonitoringAlertController())
        self._register_subcontroller(["actions"], ActionController())
        self._register_subcontroller(["groups"], HostGroupsController())

        # actions
        self._register(["provision"], self._provision, self._print_entity_completions)
        self._register(["render-tree"], self._render_tree, self._print_tree_completions)
        self._register(["clone"], self._clone, self._print_entity_completions)
        self._register(["audit"], self._audit.audit, self._print_entity_completions)
        self._register(["notification-logs"], self._notificationLog.notification_log, self._print_entity_completions)
        self._register(["agent-logs"], self._agentLog.agent_log, self._print_entity_completions)
        self._register(["other-logs"], self._otherLog.other_log, self._print_entity_completions)
        self._register(["import"], self._import, self._print_import_completions)
        self._register(["vnc"], self._vnc, self._print_entity_completions)

        self._doc = "Hosts handling."
        self._update_action_doc_params("list", "<org_name> <env_name>")
        self._update_action_doc_params("add", "<org_name>  <env_name>")
        self._update_action_doc_params("delete", "<org_name>  <env_name> <res_name>")
        self._update_action_doc_params("update", "<org_name>  <env_name> <res_name>")
        self._update_action_doc_params("show", "<org_name>  <env_name> <res_name>")
        self._register_action_doc(self._provision_doc())
        self._register_action_doc(self._render_tree_doc())
        self._register_action_doc(self._clone_doc())
        self._register_action_doc(self._audit.audit_doc())
        self._register_action_doc(self._notificationLog.notification_log_doc())
        self._register_action_doc(self._agentLog.agent_log_doc())
        self._register_action_doc(self._otherLog.other_log_doc())
        self._register_action_doc(self._vnc_doc())
        self._register_action_doc(self._import_doc())


    def get_collection(self, argv):
        if len(argv) < 2:
            raise ArgumentException("Wrong number of arguments")

        return self._client.hosts(argv[0], argv[1])

    def _print_collection_completions(self, param_num, argv):
        if param_num == 0:
            completions.print_identifiers(self._client.organizations())
        elif len(argv) > 0 and param_num == 1:
            completions.print_identifiers(self._client.environments(argv[0]))

    def _print_entity_completions(self, param_num, argv):
        if param_num < 2:
            self._print_collection_completions(param_num, argv)
        elif len(argv) > 1 and param_num == 2:
            completions.print_identifiers(self.get_collection(argv))

    def _complete_template(self, argv, template_json):
        if len(argv) < 2:
            raise ArgumentException("Wrong number of arguments")
        template_json["organization"] = argv[0]
        template_json["environment"] = argv[1]

    def _get_name_argument(self, argv):
        if len(argv) < 3:
            raise ArgumentException("Wrong number of arguments")

        return argv[2]

    def _get_value_argument(self, argv):
        if len(argv) < 4:
            return None

        return argv[3]

    def _delete(self, argv):
        host = self._get_entity(argv)

        if self._config.options.force or (prompt.confirm(prompt = "Delete " + host.name + " ?", resp = False)) :
            host.delete()

    def _print_file_completions(self, param_num, argv):
        if param_num < 3:
            self._print_entity_completions(param_num, argv)
        elif len(argv) > 2 and param_num == 3:
            completions.print_identifiers(self._client.get_host(argv[0], argv[1], argv[2]).applications())
        elif len(argv) > 3 and param_num == 4:
            completions.print_identifiers(self._client.get_application(argv[0], argv[3]).files())

    def _print_tree_completions(self, param_num, argv):
        if param_num < 3:
            self._print_entity_completions(param_num, argv)
        elif param_num == 3:
            completions.print_dir_completions()

    def _print_import_completions(self, param_num, argv):
        if param_num < 2:
            self._print_entity_completions(param_num, argv)
        elif param_num == 2:
            completions.print_dir_completions()

    def _render_tree(self, argv):
        if len(argv) != 4:
            raise MissingException("This action takes 4 arguments")

        org_name = argv[0]
        env_name = argv[1]
        host_name = argv[2]
        root_dir = argv[3]

        renderer = TreeRenderer(self._client, org_name, env_name, host_name)

        options = self._config.options
        renderer.render(root_dir, options.skip_chmod, options.skip_chown)

    def _render_tree_doc(self):
        return ActionDoc("render-tree", "<org_name> <env_name> <res_name> <output_folder>", """
        Render configuration files of given host.""")

    def _clone(self, argv):
        if len(argv) != 3:
            raise MissingException("This action takes 3 arguments")

        host = self._get_entity(argv)
        host.clone()

    def _clone_doc(self):
        return ActionDoc("clone", "<org_name> <env_name> <res_name>", """
        Clone a given host.""")

    def _provision_doc(self):
        return ActionDoc("provision", "<org_name> <env_name> <res_name>", """
        Provision a host.""")

    def _provision(self, argv):
        host = self._get_entity(argv)
        host.provision()

    def _prune_json_update(self, json_wrapper):
        super(HostsController, self)._prune_json_update(json_wrapper)
        json_wrapper._del_field("organization")
        json_wrapper._del_field("settings")
        json_wrapper._del_field("distribution")
        json_wrapper._del_field("platform")
        json_wrapper._del_field("state")

    def _vnc(self, argv):
        if len(argv) != 3:
            raise MissingException("This action takes 3 arguments")

        host = self._get_entity(argv)
        vnc_params = host.instance().get().vnc

        # Get VNC viewer call string
        config = Config()
        viewer_call_template = config.get_vnc_viewer_call(self._config.options.profile_name)
        if viewer_call_template is None or viewer_call_template == "":
            raise ControllerException("VNC viewer is not configured")

        # Call viewer
        hostname = vnc_params.hostname
        port = vnc_params.port
        if hostname != None and port != None:
            call = viewer_call_template.replace("%h", hostname).replace("%p", port)
            subprocess.call(call, shell = True)
        else:
            raise ControllerException("Could not retrieve VNC server host and/or port")

    def _vnc_doc(self):
        return ActionDoc("vnc", "<org_name> <env_name> <res_name>", """
        Executes configured VNC viewer for host's instance.""")

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
        env = self._client.environments(argv[0]).get(argv[1])



        if len(argv) < 3:
            raise ArgumentException("Wrong number of arguments")

        importer = Import(self._config.options.skip_conflict, queue_actions=True,
                          with_instances=self._config.options.with_instances)
        importer.import_full_host(org, env, argv[2])

        if self._config.options.dry_run:
            importer.display_queue(show_only_conflicts = False)

        elif (importer.no_conflict() or self._config.options.skip_conflict):
            importer.execute_queue()
        else:
            importer.display_queue(show_only_conflicts = True)
            print ("Impossible to import host. There are conflicts. Use --skip-conflict to force")

    def _import_doc(self):
        return ActionDoc("import", "<src_folder> [--dry-run]", """
            Import host from disk. With --dry-run, actions are displayed but not applied.""")
