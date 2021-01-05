# control.environments - Controller for comodit Environments entities.
# coding: utf-8
#
# Copyright 2010 Guardis SPRL, Liège, Belgium.
#
# This software cannot be used and/or distributed without prior
# authorization from Guardis.

from comodit_client.control.organization_entity import OrganizationEntityController
from comodit_client.control.actions import WebhookActionController

class WebhooksController(OrganizationEntityController):

    _template = "webhooks.json"

    def __init__(self):
        super(WebhooksController, self).__init__()
        # subcontrollers
        self._register_subcontroller(["actions"], WebhookActionController())

    # actions
                
    def _get_collection(self, org_name):
        return self._client.webhooks(org_name)

    def _prune_json_update(self, json_wrapper):
        super(WebhooksController, self)._prune_json_update(json_wrapper)
        json_wrapper._del_field("organization")
