# control.environments - Controller for cortex Environments resources.
# coding: utf-8
#
# Copyright 2010 Guardis SPRL, Liège, Belgium.
# Authors: Laurent Eschenauer <laurent.eschenauer@guardis.com>
#
# This software cannot be used and/or distributed without prior
# authorization from Guardis.

from cortex_client.util import globals
from cortex_client.control.resource import ResourceController
from cortex_client.control.exceptions import NotFoundException

class EnvironmentsController(ResourceController):

    _template = "environment.json"

    def __init__(self):
        super(EnvironmentsController, self).__init__()

    def get_collection(self):
        return self._api.get_environment_collection()

    def _get_resources(self, argv):
        options = globals.options
        parameters = {}

        # Validate input parameters
        org_uuid = None
        if options.org_uuid:
            org_uuid = options.org_uuid
        elif options.org_path:
            path = options.env_path
            org_uuid = self._api.get_directory().get_organization_uuid(path)
            if not org_uuid: raise NotFoundException(path)
        elif options.org and options.uuid:
            org_uuid = options.env
        elif options.org:
            path = options.org
            org_uuid = self._api.get_directory().get_organization_uuid(path)
            if not org_uuid: raise NotFoundException(path)

        if(org_uuid):
            parameters["organizationId"] = org_uuid

        return super(EnvironmentsController, self)._get_resources(argv, parameters)

    def _help(self, argv):
        print '''You must provide an action to perform on this resource.

Actions:
    list [--org <id> | --org-uuid <uuid> | --org-path <path>]
                    List all environments, possibly within a given organization
    show <id>       Show the details of an environment
    add             Add an environment
    update <id>     Update an environment
    delete <id>     Delete an environment
'''
