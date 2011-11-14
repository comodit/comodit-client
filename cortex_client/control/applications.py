# control.applications - Controller for cortex Applications resources.
# coding: utf-8
#
# Copyright 2010 Guardis SPRL, Liège, Belgium.
# Authors: Laurent Eschenauer <laurent.eschenauer@guardis.com>
#
# This software cannot be used and/or distributed without prior
# authorization from Guardis.

from cortex_client.control.resource import ResourceController
from cortex_client.control.exceptions import MissingException

class ApplicationsController(ResourceController):

    _template = "application.json"

    def __init__(self):
        super(ApplicationsController, self).__init__()
        self._register(["show-file"], self._show_file)
        self._register(["set-file"], self._set_file)

    def get_collection(self):
        return self._api.get_application_collection()

    def _show_file(self, argv):
        app = self._get_resource(argv)
        file_name = argv[1]
        print app.get_file_content(file_name).read()

    def _set_file(self, argv):
        dist = self._get_resource(argv)

        if len(argv) != 3:
            raise MissingException("Wrong number of arguments")

        dist.set_file_content(argv[1], argv[2])

    def _help(self, argv):
        print '''You must provide an action to perform on this resource.

Actions:
    list            List all application profiles available to the user
    show <id>       Show the details of an application profile
    show-file <id> <name>
                    Show the content of a file resource's template
    set-file <id> <name> <path>
                    Update the content of a file resource's template
    add             Add an application profile
    update <id>     Update an application profile
    delete <id>     Delete an application profile
'''
