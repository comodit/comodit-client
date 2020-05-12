# control.environments - Controller for comodit Environments entities.
# coding: utf-8
#
# Copyright 2010 Guardis SPRL, Liège, Belgium.
#
# This software cannot be used and/or distributed without prior
# authorization from Guardis.

from comodit_client.control.organization_entity import OrganizationEntityController


class HostGroupController(OrganizationEntityController):

    _template = "host_group.json"

    def __init__(self):
        super(HostGroupController, self).__init__()
        # subcontrollers
        # actions

    def _get_collection(self, org_name):
        return self._client.host_groups(org_name)

    def _prune_json_update(self, json_wrapper):
        super(HostGroupController, self)._prune_json_update(json_wrapper)
        json_wrapper._del_field("organization")
