# control.users - Controller for cortex Users resources.
# coding: utf-8
#
# Copyright 2010 Guardis SPRL, Liège, Belgium.
# Authors: Laurent Eschenauer <laurent.eschenauer@guardis.com>
#
# This software cannot be used and/or distributed without prior
# authorization from Guardis.

from cortex_client.control.root_resource import RootResourceController

class UsersController(RootResourceController):

    _template = "user.json"

    def __init__(self):
        super(UsersController, self).__init__()

        self._doc = "Users handling."

    def get_collection(self, argv):
        return self._api.users()
