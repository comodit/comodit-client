# control.environments - Controller for comodit Environments entities.
# coding: utf-8
#
# Copyright 2010 Guardis SPRL, Liège, Belgium.
#
# This software cannot be used and/or distributed without prior
# authorization from Guardis.
from comodit_client.control import completions
from comodit_client.control.entity import EntityController
from comodit_client.control.exceptions import ArgumentException


class OrchestrationHandlerController(EntityController):

    _template = "orchestration_handler.json"

    def __init__(self):
        super(OrchestrationHandlerController, self).__init__()
        # subcontrollers

    # actions

    def get_collection(self, argv):
        return self._client.orchestration_handlers(argv[0], argv[1])

    def _print_collection_completions(self, param_num, argv):
        if param_num == 0:
            completions.print_identifiers(self._client.organizations())
        elif len(argv) > 0 and param_num == 1:
            completions.print_identifiers(self._client.orchestrations(argv[0]))

    def _print_entity_completions(self, param_num, argv):
        if param_num < 2:
            self._print_collection_completions(param_num, argv)
        elif len(argv) > 1 and param_num == 2:
            completions.print_identifiers(self.get_collection(argv))

    def _prune_json_update(self, json_wrapper):
        super(OrchestrationHandlerController, self)._prune_json_update(json_wrapper)
        json_wrapper._del_field("organization")

    def _get_name_argument(self, argv):
        if len(argv) < 3:
            raise ArgumentException("Wrong number of arguments")

        return argv[2]
