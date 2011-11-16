# control.applications - Controller for cortex Applications resources.
# coding: utf-8
#
# Copyright 2010 Guardis SPRL, Liège, Belgium.
# Authors: Laurent Eschenauer <laurent.eschenauer@guardis.com>
#
# This software cannot be used and/or distributed without prior
# authorization from Guardis.

from cortex_client.control.resource import ResourceController

class PlatformsController(ResourceController):

    _template = "platform.json"

    def __init__(self):
        super(PlatformsController, self).__init__()

    def get_collection(self):
        return self._api.get_platform_collection()

    def _help(self, argv):
        print '''You must provide an action to perform on this resource.

Actions:
    list            List all platforms available to the user
    show <id>       Show the details of a platform
    add             Add a platform
    update <id>     Update a platform
    delete <id>     Delete a platform
'''
