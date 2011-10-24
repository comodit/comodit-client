# control.applications - Controller for cortex Applications resources.
# coding: utf-8
#
# Copyright 2010 Guardis SPRL, Liège, Belgium.
# Authors: Laurent Eschenauer <laurent.eschenauer@guardis.com>
#
# This software cannot be used and/or distributed without prior
# authorization from Guardis.

from cortex_client.control.resource import ResourceController

class ChangesController(ResourceController):

    _template = "change.json"

    def __init__(self):
        super(ChangesController, self ).__init__()
        self._register(["apply"], self._apply)

    def get_collection(self):
        return self._api.get_change_request_collection()

    def _apply(self, argv):
        change_req = self._get_resource(argv)
        change_req.apply_request()

    def _help(self, argv):
        print '''You must provide an action to perform on this resource.

Actions:
    list              List all change requests available to the user
    show <uuid>       Show the details of a change request
    add               Add a change request
    update <uuid>     Update a change request
    delete <uuid>     Delete a change request
    apply <uuid>      Apply a change request
'''
