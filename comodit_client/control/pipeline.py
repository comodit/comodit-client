# control.environments - Controller for comodit Environments entities.
# coding: utf-8
#
# Copyright 2010 Guardis SPRL, Liège, Belgium.
#
# This software cannot be used and/or distributed without prior
# authorization from Guardis.

from comodit_client.control.organization_entity import OrganizationEntityController
from comodit_client.control.actions import PipelineActionController
from comodit_client.control.entity import EntityController
from comodit_client.control import completions
from comodit_client.api.stage import StageCollection


class PipelineController(OrganizationEntityController):

    _template = "pipeline.json"

    def __init__(self):
        super(PipelineController, self).__init__()
        # subcontrollers
        self._register_subcontroller(["stages"], StageController())
        self._register_subcontroller(["actions"], PipelineActionController())

    # actions
                
    def _get_collection(self, org_name):
        return self._client.pipelines(org_name)

    def _prune_json_update(self, json_wrapper):
        super(PipelineController, self)._prune_json_update(json_wrapper)
        json_wrapper._del_field("organization")


class StageController(EntityController):
    _template = "stage.json"

    def __init__(self):
        super(StageController, self).__init__()
    # actions
        self._register_subcontroller(["steps"], StepController())

    def _print_collection_completions(self, param_num, argv):
        if param_num == 0:
            completions.print_identifiers(self._client.organizations())
        elif len(argv) > 0 and param_num == 1:
            completions.print_identifiers(self._client.pipelines(argv[0]))
        elif len(argv) > 0 and param_num == 2:
            completions.print_identifiers(self._client.pipeline(argv[0], argv[1]).stages)


    def _print_entity_completions(self, param_num, argv):
        if param_num < 2:
            self._print_collection_completions(param_num, argv)
        elif len(argv) > 1 and param_num == 2:
            completions.print_identifiers(self.get_collection(argv))

    def get_collection(self, argv):
        if len(argv) < 2:
            raise ArgumentException("Wrong number of arguments")

        return self._client.stages(argv[0], argv[1])

    def _get_name_argument(self, argv):
        if len(argv) < 3:
            raise ArgumentException("Wrong number of arguments")

        return argv[2]

class StepController(EntityController):
    _template = "step.json"

    def __init__(self):
        super(StepController, self).__init__()
    # actions

    def _print_collection_completions(self, param_num, argv):
        if param_num == 0:
            completions.print_identifiers(self._client.organizations())
        elif len(argv) > 0 and param_num == 1:
            completions.print_identifiers(self._client.pipelines(argv[0]))
        elif len(argv) > 0 and param_num == 2:
            completions.print_identifiers(self._client.pipeline(argv[0], argv[1]).stages)
        elif len(argv) > 0 and param_num == 3:
            completions.print_identifiers(self._client.stage(argv[0], argv[1], argv[2]).steps)


    def _print_entity_completions(self, param_num, argv):
        if param_num < 4:
            self._print_collection_completions(param_num, argv)
        elif len(argv) > 1 and param_num == 2:
            completions.print_identifiers(self.get_collection(argv))

    def get_collection(self, argv):
        if len(argv) < 2:
            raise ArgumentException("Wrong number of arguments")

        return self._client.steps(argv[0], argv[1], argv[2])

    def _get_name_argument(self, argv):
        if len(argv) < 4:
            raise ArgumentException("Wrong number of arguments")

        return argv[3]