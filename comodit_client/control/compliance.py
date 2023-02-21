# control.applications - Controller for comodit Applications entities.
# coding: utf-8
#
# Copyright 2010 Guardis SPRL, Liège, Belgium.
# Authors: Laurent Eschenauer <laurent.eschenauer@guardis.com>
#
# This software cannot be used and/or distributed without prior
# authorization from Guardis.

from __future__ import absolute_import

from comodit_client.control.doc import ActionDoc
from comodit_client.control.entity import EntityController
from comodit_client.control.exceptions import ArgumentException

from . import completions


class ComplianceController(EntityController):

    def __init__(self):
        super(ComplianceController, self).__init__()
        self._doc = "Compliance errors handling."

        self._unregister("add")
        self._unregister("update")

        self._register(["delete-all"], self._delete_all, self._print_collection_completions)
        self._register(["rebuild"], self._rebuild, self._print_collection_completions)

        self._register_action_doc(self._delete_all_doc())
        self._register_action_doc(self._rebuild_doc())

    def get_collection(self, argv):
        if len(argv) < 3:
            raise ArgumentException("Wrong number of arguments");
        return self._client.get_host(argv[0], argv[1], argv[2]).compliance()

    def _print_collection_completions(self, param_num, argv):
        if param_num == 0:
            completions.print_identifiers(self._client.organizations())
        elif len(argv) > 0 and param_num == 1:
            completions.print_identifiers(self._client.environments(argv[0]))
        elif len(argv) > 1 and param_num == 2:
            completions.print_identifiers(self._client.hosts(argv[0], argv[1]))

    def _print_entity_completions(self, param_num, argv):
        if param_num < 3:
            self._print_collection_completions(param_num, argv)
        elif len(argv) > 2 and param_num == 3:
            for e in self._client.get_host(argv[0], argv[1], argv[2]).compliance():
                completions.print_escaped_string(e.identifier)

    def _show_doc(self):
        return ActionDoc("show", "<org_name> <env_name> <host_name> <applications/<app_name>/<type>/<id>>", """
        Show an entity.""")

    def _delete_doc(self):
        return ActionDoc("delete", "<org_name> <env_name> <host_name> <applications/<app_name>/<type>/<id>>", """
        Delete an existing entity.""")


    def _get_name_argument(self, argv):
        if len(argv) < 4:
            raise ArgumentException("An organization, environment, host and compliance error name must be provided")
        return argv[3]

    def _delete_all(self, argv):
        compliance = self.get_collection(argv)
        compliance.clear()

    def _delete_all_doc(self):
        return ActionDoc("delete-all", "<org_name> <env_name> <host_name>", """
        Deletes all compliance errors.""")

    def _rebuild(self, argv):
        compliance = self.get_collection(argv)
        compliance.rebuild()

    def _rebuild_doc(self):
        return ActionDoc("rebuild", "<org_name> <env_name> <host_name>", """
        Rebuilds compliance DB by sending back all state info to agent.""")
