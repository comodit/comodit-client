# control.distributions - Controller for comodit Distributions entities.
# coding: utf-8
#
# Copyright 2010 Guardis SPRL, Liège, Belgium.
# Authors: Laurent Eschenauer <laurent.eschenauer@guardis.com>
#
# This software cannot be used and/or distributed without prior
# authorization from Guardis.

from __future__ import absolute_import
from comodit_client.api.exporter import Export
from comodit_client.api.importer import Import
from comodit_client.control.doc import ActionDoc
from comodit_client.control.exceptions import ArgumentException
from comodit_client.control.files import DistributionFilesController
from comodit_client.control.organization_entity import OrganizationEntityController
from comodit_client.control.parameters import DistributionParametersController
from comodit_client.control.settings import DistributionSettingsController
from comodit_client.control.store_helper import StoreHelper
from comodit_client.control.sync import DistSyncController
from . import completions
from ..util import prompt


class DistributionsController(OrganizationEntityController):

    _template = "distribution.json"

    def __init__(self):
        super(DistributionsController, self).__init__()

        # subcontrollers
        self._register_subcontroller(["settings"], DistributionSettingsController())
        self._register_subcontroller(["files"], DistributionFilesController())
        self._register_subcontroller(["parameters"], DistributionParametersController())
        self._register_subcontroller(["sync"], DistSyncController())
        self._register(["lock"], self._lock, self._print_entity_completions)
        self._register(["unlock"], self._unlock, self._print_entity_completions)

        self._doc = "Distributions handling."

        # actions
        self._register(["import"], self._import, self._print_import_completions)
        self._register(["export"], self._export, self._print_export_completions)

        helper = StoreHelper(self, "dist")
        self._register(["publish"], helper._publish, self._print_entity_completions)
        self._register(["unpublish"], helper._unpublish, self._print_entity_completions)
        self._register(["push"], helper._push, self._print_entity_completions)
        self._register(["pull"], helper._pull, self._print_entity_completions)
        self._register(["update-authorized"], helper._update_authorized, self._print_entity_completions)

        self._register_action_doc(self._export_doc())
        self._register_action_doc(self._import_doc())
        self._register_action_doc(helper._publish_doc())
        self._register_action_doc(helper._unpublish_doc())
        self._register_action_doc(helper._push_doc())
        self._register_action_doc(helper._pull_doc())
        self._register_action_doc(self._lock_doc())
        self._register_action_doc(self._unlock_doc())
        self._register_action_doc(helper._update_authorized_doc())

    def _get_collection(self, org_name):
        return self._client.distributions(org_name)

    def _lock_doc(self):
        return ActionDoc("lock"," <org_name> <dist_name>", """
        Lock disable update.""")

    def _unlock_doc(self):
        return ActionDoc("unlock", "<org_name> <dist_name> [--force]", """
        Unlock enable update.""")


    def _prune_json_update(self, json_wrapper):
        super(DistributionsController, self)._prune_json_update(json_wrapper)
        json_wrapper._del_field("organization")
        json_wrapper._del_field("settings")
        json_wrapper._del_field("files")
        json_wrapper._del_field("parameters")

    # Export

    def _print_export_completions(self, param_num, argv):
        if param_num < 2:
            self._print_entity_completions(param_num, argv)
        elif param_num == 2:
            completions.print_dir_completions()

    def _export(self, argv):
        self._options = self._config.options

        dist = self._get_entity(argv)

        root_folder = dist.name
        if len(argv) > 2:
            root_folder = argv[2]

        export = Export(self._config.options.force)
        export.export_distribution(dist, root_folder)

    def _export_doc(self):
        return ActionDoc("export", "<org_name> <dist_name> [<output_folder>] [--force]", """
        Export distribution onto disk. --force option causes existing files to
        be overwritten.""")

    # Import

    def _print_import_completions(self, param_num, argv):
        if param_num < 1:
            self._print_collection_completions(param_num, argv)
        elif param_num == 1:
            completions.print_dir_completions()

    def _import(self, argv):
        if len(argv) != 2:
            raise ArgumentException("Wrong number of arguments")

        org = self._client.get_organization(argv[0])
        imp = Import(update_existing=self._config.options.update_existing)
        imp.import_distribution(org, argv[1])

    def _import_doc(self):
        return ActionDoc("import", "<org_name> <src_folder> [--update-existing]", """
        Import distribution from disk. --update-existing option causes existing entities
        on server to be updated.""")

    def _complete_template(self, argv, template_json):
        flavor_name = self._config.options.flavor
        if flavor_name != None:
            template_json["settings"] = []
            flavor = self._client.get_flavor(flavor_name)
            for p in flavor.parameters_f:
                template_json["settings"].append({"key": p.key, "value":p.value})

    def _lock(self, argv):
        dist = self._get_entity(argv)
        dist.lock()

    def _unlock(self, argv):
        dist = self._get_entity(argv)
        if not dist.locked :
            print("distribution not locked")
        elif self._config.options.force or (prompt.confirm(prompt="Unlock " + dist.name + " ?", resp=False)) :
            dist.unlock()

