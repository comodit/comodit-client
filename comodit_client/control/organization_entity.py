# control.distributions - Controller for comodit Distributions entities.
# coding: utf-8
#
# Copyright 2011 Guardis SPRL, Liège, Belgium.
# Authors: Gérard Dethier <gerard.dethier@guardis.com>
#
# This software cannot be used and/or distributed without prior
# authorization from Guardis.

from __future__ import absolute_import

from comodit_client.control.doc import ActionDoc
from comodit_client.control.entity import EntityController
from comodit_client.control.exceptions import ArgumentException

from . import completions


class OrganizationEntityController(EntityController):

    def __init__(self):
        super(OrganizationEntityController, self).__init__()

        # action
        self._register(["clone"], self._clone, self._print_entity_completions)

        self._update_action_doc_params("list", "<org_name>")
        self._update_action_doc_params("add", "<org_name>")
        self._update_action_doc_params("delete", "<org_name> <res_name>")
        self._update_action_doc_params("update", "<org_name> <res_name>")
        self._update_action_doc_params("show", "<org_name> <res_name>")
        self._register_action_doc(self._clone_doc())

    def _get_name_argument(self, argv):
        if len(argv) < 2:
            raise ArgumentException("An organization name must be provided, in addition to entity name");
        return argv[1]

    def _get_value_argument(self, argv):
        if len(argv) < 3:
            return None

        return argv[2]

    def _get_collection(self, org_name):
        raise NotImplementedError

    def get_collection(self, argv):
        if len(argv) == 0:
            raise ArgumentException("An organization name must be provided");

        return self._get_collection(argv[0])

    def _print_collection_completions(self, param_num, argv):
        if param_num == 0:
            completions.print_identifiers(self._client.organizations())

    def _print_entity_completions(self, param_num, argv):
        if param_num < 1:
            self._print_collection_completions(param_num, argv)
        elif len(argv) > 0 and param_num == 1:
            completions.print_identifiers(self._get_collection(argv[0]))

    def _print_list_completions(self, param_num, argv):
        self._print_collection_completions(param_num, argv)

    def _print_show_completions(self, param_num, argv):
        self._print_entity_completions(param_num, argv)

    def _print_add_completions(self, param_num, argv):
        self._print_collection_completions(param_num, argv)

    def _print_update_completions(self, param_num, argv):
        self._print_entity_completions(param_num, argv)

    def _print_delete_completions(self, param_num, argv):
        self._print_entity_completions(param_num, argv)

    def _clone(self, argv):
        if len(argv) < 3:
            raise ArgumentException("Expected 3 arguments")

        res = self._get_entity(argv)
        res.clone(argv[2])

    def _clone_doc(self):
        return ActionDoc("clone", "<org_name> <res_name> <clone_name>", """
        Clone an entity.""")

