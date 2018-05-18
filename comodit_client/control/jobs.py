# control.environments - Controller for comodit Environments entities.
# coding: utf-8
#
# Copyright 2010 Guardis SPRL, Liège, Belgium.
# Authors: Laurent Eschenauer <laurent.eschenauer@guardis.com>
#
# This software cannot be used and/or distributed without prior
# authorization from Guardis.

from comodit_client.control.organization_entity import OrganizationEntityController

class JobsController(OrganizationEntityController):

    _template = "jobs.json"

    def __init__(self):
        super(JobsController, self).__init__()

        # subcontrollers

        # actions

    def _get_collection(self, org_name):
        return self._client.jobs(org_name)

    def _prune_json_update(self, json_wrapper):
        super(JobsController, self)._prune_json_update(json_wrapper)
        json_wrapper._del_field("organization")
