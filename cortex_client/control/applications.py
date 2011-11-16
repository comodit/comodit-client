# control.applications - Controller for cortex Applications resources.
# coding: utf-8
#
# Copyright 2010 Guardis SPRL, Liège, Belgium.
# Authors: Laurent Eschenauer <laurent.eschenauer@guardis.com>
#
# This software cannot be used and/or distributed without prior
# authorization from Guardis.

from cortex_client.control.resource import ResourceController

class ApplicationsController(ResourceController):

    _template = "application.json"

    def __init__(self):
        super(ApplicationsController, self).__init__()

    def get_collection(self):
        return self._api.get_application_collection()

    def _help(self, argv):
        print '''You must provide an action to perform on this resource.

Actions:
    list            List all application profiles available to the user
    show <id>       Show the details of an application profile
    add             Add an application profile
    update <id>     Update an application profile
    delete <id>     Delete an application profile
'''
