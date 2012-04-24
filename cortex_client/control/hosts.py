# control.hosts - Controller for cortex Hosts resources.
# coding: utf-8
#
# Copyright 2010 Guardis SPRL, Liège, Belgium.
# Authors: Laurent Eschenauer <laurent.eschenauer@guardis.com>
#
# This software cannot be used and/or distributed without prior
# authorization from Guardis.

import subprocess

from cortex_client.util import prompt, globals
from cortex_client.control.resource import ResourceController
from cortex_client.control.exceptions import ArgumentException, MissingException
from cortex_client.control.settings import HostSettingsController
from cortex_client.control.instances import InstancesController
from cortex_client.control.contexts import PlatformContextController, \
    DistributionContextController, ApplicationContextController
from cortex_client.control.tree_rendering import TreeRenderer
from cortex_client.control.doc import ActionDoc
from cortex_client.api import collections
from cortex_client.control.audit import AuditHelper
from cortex_client.config import Config


class HostsController(ResourceController):

    _template = "host.json"

    def __init__(self):
        super(HostsController, self).__init__()
        self._audit = AuditHelper(self, "<org_name> <env_name> <res_name>")

        # subcontrollers
        self._register_subcontroller(["settings"], HostSettingsController())
        self._register_subcontroller(["instance"], InstancesController())
        self._register_subcontroller(["applications"], ApplicationContextController())
        self._register_subcontroller(["distribution"], DistributionContextController())
        self._register_subcontroller(["platform"], PlatformContextController())

        # actions
        self._register(["provision"], self._provision, self._print_resource_completions)
        self._register(["render-tree"], self._render_tree, self._print_tree_completions)
        self._register(["clone"], self._clone, self._print_resource_completions)
        self._register(["changes"], self._changes, self._print_resource_completions)
        self._register(["all-changes"], self._all_changes, self._print_resource_completions)
        self._register(["clear-changes"], self._clear_changes, self._print_resource_completions)
        self._register(["audit"], self._audit.audit, self._print_resource_completions)
        self._register(["vnc"], self._vnc, self._print_resource_completions)

        self._doc = "Hosts handling."
        self._update_action_doc_params("list", "<org_name> <env_name>")
        self._update_action_doc_params("add", "<org_name>  <env_name>")
        self._update_action_doc_params("delete", "<org_name>  <env_name> <res_name>")
        self._update_action_doc_params("update", "<org_name>  <env_name> <res_name>")
        self._update_action_doc_params("show", "<org_name>  <env_name> <res_name>")
        self._register_action_doc(self._provision_doc())
        self._register_action_doc(self._render_tree_doc())
        self._register_action_doc(self._clone_doc())
        self._register_action_doc(self._changes_doc())
        self._register_action_doc(self._clear_changes_doc())
        self._register_action_doc(self._audit.audit_doc())
        self._register_action_doc(self._vnc_doc())

    def get_collection(self, argv):
        if len(argv) < 2:
            raise ArgumentException("Wrong number of arguments");

        return collections.hosts(self._api, argv[0], argv[1])

    def _print_collection_completions(self, param_num, argv):
        if param_num == 0:
            self._print_identifiers(self._api.organizations())
        elif len(argv) > 0 and param_num == 1:
            self._print_identifiers(collections.environments(self._api, argv[0]))

    def _print_resource_completions(self, param_num, argv):
        if param_num < 2:
            self._print_collection_completions(param_num, argv)
        elif len(argv) > 1 and param_num == 2:
            self._print_identifiers(self.get_collection(argv))

    def _complete_template(self, argv, template_json):
        if len(argv) < 2:
            raise ArgumentException("Wrong number of arguments");
        template_json["organization"] = argv[0]
        template_json["environment"] = argv[1]

    def _get_name_argument(self, argv):
        if len(argv) < 3:
            raise ArgumentException("Wrong number of arguments");

        return argv[2]

    def _delete(self, argv):
        host = self._get_resource(argv)

        if globals.options.force or (prompt.confirm(prompt = "Delete " + host.get_name() + " ?", resp = False)) :
            host.delete()

    def _print_file_completions(self, param_num, argv):
        if param_num < 3:
            self._print_resource_completions(param_num, argv)
        elif len(argv) > 2 and param_num == 3:
            self._print_escaped_names(collections.application_contexts(self._api, argv[0], argv[1], argv[2]))
        elif len(argv) > 3 and param_num == 4:
            self._print_escaped_name(collections.application_files(self._api, argv[0], argv[3]))

    def _print_tree_completions(self, param_num, argv):
        if param_num < 3:
            self._print_resource_completions(param_num, argv)
        elif param_num == 3:
            self._print_dir_completions()

    def _render_tree(self, argv):
        if len(argv) != 4:
            raise MissingException("This action takes 4 arguments")

        org_name = argv[0]
        env_name = argv[1]
        host_name = argv[2]
        root_dir = argv[3]

        renderer = TreeRenderer(self._api, org_name, env_name, host_name)

        options = globals.options
        renderer.render(root_dir, options.skip_chmod, options.skip_chown)

    def _render_tree_doc(self):
        return ActionDoc("render-tree", "<org_name> <env_name> <res_name> <output_folder>", """
        Render configuration files of given host.""")

    def _clone(self, argv):
        if len(argv) != 3:
            raise MissingException("This action takes 3 arguments")

        host = self._get_resource(argv)
        host.clone()

    def _clone_doc(self):
        return ActionDoc("clone", "<org_name> <env_name> <res_name>", """
        Clone a given host.""")

    def _changes(self, argv):
        if len(argv) != 3:
            raise MissingException("This action takes 3 arguments")

        host = self._get_resource(argv)
        changes = host.get_changes()
        print "Changes:"
        for c in changes:
            c.show()

    def _all_changes(self, argv):
        if len(argv) != 3:
            raise MissingException("This action takes 3 arguments")

        host = self._get_resource(argv)
        changes = host.get_changes(show_processed = True)
        print "Changes:"
        for c in changes:
            c.show()

    def _changes_doc(self):
        return ActionDoc("changes", "<org_name> <env_name> <res_name>", """
        Display pending changes of a given host.""")

    def _clear_changes(self, argv):
        if len(argv) != 3:
            raise MissingException("This action takes 3 arguments")

        host = self._get_resource(argv)
        host.clear_changes()

    def _clear_changes_doc(self):
        return ActionDoc("clear-changes", "<org_name> <env_name> <res_name>", """
        Clear pending changes of a given host.""")

    def _provision_doc(self):
        return ActionDoc("provision", "<org_name> <env_name> <res_name>", """
        Provision a host.""")

    def _provision(self, argv):
        host = self._get_resource(argv)
        host.provision()

    def _prune_json_update(self, json_wrapper):
        super(HostsController, self)._prune_json_update(json_wrapper)
        json_wrapper._del_field("organization")
        json_wrapper._del_field("environment")
        json_wrapper._del_field("settings")
        json_wrapper._del_field("applications")
        json_wrapper._del_field("distribution")
        json_wrapper._del_field("platform")
        json_wrapper._del_field("state")

    def _vnc(self, argv):
        if len(argv) != 3:
            raise MissingException("This action takes 3 arguments")

        host = self._get_resource(argv)
        vnc_params = host.instance().get_single_resource().get_vnc()

        # Get VNC viewer call string
        profile = Config().get_profile(globals.options.profile_name)
        viewer_call_template = profile.get("vnc_viewer_call")
        if viewer_call_template is None or viewer_call_template == "":
            print "VNC viewer is not configured"
            return

        # Call viewer
        call = viewer_call_template.replace("%h", vnc_params.get_hostname()).replace("%p", vnc_params.get_port())
        subprocess.call(call, shell = True)

    def _vnc_doc(self):
        return ActionDoc("vnc", "<org_name> <env_name> <res_name>", """
        Executes configured VNC viewer for host's instance.""")
