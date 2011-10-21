# control.users - Controller for cortex Users resources.
# coding: utf-8
#
# Copyright 2010 Guardis SPRL, Liège, Belgium.
# Authors: Laurent Eschenauer <laurent.eschenauer@guardis.com>
#
# This software cannot be used and/or distributed without prior
# authorization from Guardis.

from cortex_client.control.resource import ResourceController

class UsersController(ResourceController):

    _template = "user.json"

    def __init__(self):
        super(UsersController, self ).__init__()

    def get_collection(self):
        return self._api.get_user_collection()

    def _help(self, argv):
        print '''You must provide an action to perfom on this resource.

Actions:
    list            List all users
    show <id>       Show the details of a user
    add             Add a user
    update <id>     Update a user
    delete <id>     Delete a user

<id> is either a UUID (--with-uuid option must be provided), either a user name.

'''
