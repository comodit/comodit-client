# control.orchetsrationContext - Controller for comodit orchestration contexts entities.
# coding: utf-8
#
# Copyright 2010 Guardis SPRL, Liège, Belgium.
#
# This software cannot be used and/or distributed without prior
# authorization from Guardis.

from __future__ import absolute_import
from comodit_client.control.abstract import AbstractController
from comodit_client.control.doc import ActionDoc
from . import completions
import json


class OrchestrationContextController(AbstractController):

    def __init__(self):
        super(OrchestrationContextController, self).__init__()
        self._doc = "History of orchestration execution"

        self._register(["list"], self._list, self._print_list_completions)
        self._register(["show"], self._show, self._print_show_completions)

        self._register(["help"], self._help)
        self._default_action = self._help

        self._register_action_doc(self._list_doc())
        self._register_action_doc(self._show_doc())

    def _help(self, argv):
        self._print_doc()

    def _list_doc(self):
        return ActionDoc("list", "<org_name> <orchestration_name> ", """
        list all executions of orchestration.""")

    def _show_doc(self):
        return ActionDoc("show", "<org_name> <orchestration_name> <context_id> ", """
        show detail of execution of orchestration.""")

    def _print_list_completions(self, param_num, argv):
        if param_num == 0:
            completions.print_entity_identifiers(self._client.organizations().list())
        elif len(argv) > 0 and param_num == 1:
            completions.print_entity_identifiers(self._client.orchestrations(argv[0]).list())

    def _print_show_completions(self, param_num, argv):
        if param_num < 2:
            self._print_list_completions(param_num, argv)
        elif len(argv) > 1:
            contexts = self._client.orchestrationContexts(argv[0], argv[1])
            for res in contexts:
                completions.print_escaped_string(res.identifier)

    def _list(self, argv):
        contexts = self._client.orchestrationContexts(argv[0], argv[1])
        raw = self._config.options.raw
        status = self._config.options.status
        for c in contexts:
            if status :
                if c.status.lower() == status.lower():
                    self._show_identifier(raw, c)
            else:
                self._show_identifier(raw, c)

    def _show_identifier(self, raw, context):
        if raw:
            print(json.dumps(context.get_json(), indent=4))
        else :
            context.show_identifier()


    def _show(self, argv):
        context = self._client.orchestrationContext(argv[0], argv[1], argv[2])
        options = self._config.options
        context.show(options.raw, 2)