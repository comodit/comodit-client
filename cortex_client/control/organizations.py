# control.organizations - Controller for cortex Organizations resources.
# coding: utf-8
#
# Copyright 2010 Guardis SPRL, Liège, Belgium.
# Authors: Laurent Eschenauer <laurent.eschenauer@guardis.com>
#
# This software cannot be used and/or distributed without prior
# authorization from Guardis.

from cortex_client.control.resource import ResourceController

class OrganizationsController(ResourceController):

    _template = "organization.json"

    def __init__(self):
        super(OrganizationsController, self ).__init__()

    def get_collection(self):
        return self._api.get_organization_collection()

    def _help(self, argv):
        print '''You must provide an action to perfom on this resource.

Actions:
    list            List all organizations visible to the user
    show [id]       Show the details of an organization
    add             Add an organization
    update [id]     Update an organization
    delete [id]     Delete an organization
'''
