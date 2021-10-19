# control.applications - Controller for comodit Applications entities.
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
from comodit_client.control.files import ApplicationFilesController
from comodit_client.control.organization_entity import OrganizationEntityController
from comodit_client.control.parameters import ApplicationParametersController
from comodit_client.control.store_helper import StoreHelper
from comodit_client.control.sync import AppSyncController
from . import completions
from comodit_client.util import prompt
from .rpmmodules import RpmModuleController


class ApplicationsController(OrganizationEntityController):

    _template = "application.json"

    def __init__(self):
        super(ApplicationsController, self).__init__()

        # sub-controllers
        self._register_subcontroller(["files"], ApplicationFilesController())
        self._register_subcontroller(["parameters"], ApplicationParametersController())
        self._register_subcontroller(["rpm-module"], RpmModuleController())
        self._register_subcontroller(["sync"], AppSyncController())
        self._register(["lock"], self._lock, self._print_entity_completions)
        self._register(["unlock"], self._unlock, self._print_entity_completions)

        self._doc = "Applications handling."

        # actions
        self._register(["import"], self._import, self._print_import_completions)
        self._register(["export"], self._export, self._print_export_completions)

        helper = StoreHelper(self, "app")
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
        return self._client.applications(org_name)

    def _lock_doc(self):
        return ActionDoc("lock"," <org_name> <app_name>", """
        Lock disable update.""")

    def _unlock_doc(self):
        return ActionDoc("unlock", "<org_name> <app_name> [--force]", """
        Unlock enable update.""")


    def _prune_json_update(self, json_wrapper):
        super(ApplicationsController, self)._prune_json_update(json_wrapper)
        json_wrapper._del_field("organization")
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

        app = self._get_entity(argv)

        root_folder = app.name
        if len(argv) > 2:
            root_folder = argv[2]

        export = Export(self._config.options.force)
        export.export_application(app, root_folder)

    def _export_doc(self):
        return ActionDoc("export", "<org_name> <app_name> [<output_folder>] [--force]", """
        Export application onto disk. --force option causes existing files to
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
        imp.import_application(org, argv[1])

    def _import_doc(self):
        return ActionDoc("import", "<org_name> <src_folder> [--update-existing]", """
        Import application from disk. --update-existing option causes existing entities
        on server to be updated.""")

    def _lock(self, argv):
        app = self._get_entity(argv)
        app.lock()

    def _unlock(self, argv):
        app = self._get_entity(argv)
        if not app.locked :
            print("application not locked")
        elif self._config.options.force or (prompt.confirm(prompt="Unlock " + app.name + " ?", resp=False)) :
            app.unlock()
