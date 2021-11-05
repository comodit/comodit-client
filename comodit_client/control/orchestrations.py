# control.environments - Controller for comodit Environments entities.
# coding: utf-8
#
# Copyright 2010 Guardis SPRL, Liège, Belgium.
#
# This software cannot be used and/or distributed without prior
# authorization from Guardis.

from comodit_client.control.organization_entity import OrganizationEntityController
from comodit_client.control.actions import OrchestrationActionController
from comodit_client.control.orchestration_handler import OrchestrationHandlerController


class OrchestrationsController(OrganizationEntityController):
    _template = "orchestrations.json"

    def __init__(self):
        super(OrchestrationsController, self).__init__()
        # subcontrollers
        self._register_subcontroller(["actions"], OrchestrationActionController())
        self._register_subcontroller(["handlers"], OrchestrationHandlerController())

    # actions

    def _get_collection(self, org_name):
        return self._client.orchestration(org_name, )

    def _prune_json_update(self, json_wrapper):
        super(OrchestrationsController, self)._prune_json_update(json_wrapper)
        json_wrapper._del_field("organization")
