# control.users - Controller for cortex Users resources.
# coding: utf-8
#
# Copyright 2010 Guardis SPRL, Liège, Belgium.
# Authors: Laurent Eschenauer <laurent.eschenauer@guardis.com>
#
# This software cannot be used and/or distributed without prior
# authorization from Guardis.

import sys, json

from cortex_client.util import globals, prompt
from cortex_client.control.resource import ResourceController
from cortex_client.control.exceptions import ControllerException
from cortex_client.control.exceptions import NotFoundException, MissingException
from cortex_client.rest.client import Client

class UsersController(ResourceController):

    _resource = "users"
    _template = "user.json"

    def __init__(self):
        super(UsersController, self ).__init__()

    def _render(self, item, detailed=False):
        if not detailed:
            print item['uuid'], item['username']
        else:
            print "Username:", item['username']
            print "UUID:", item['uuid']
            sys.stdout.write("Roles: ")
            map(lambda x: sys.stdout.write(x+ " "), item['roles'])
            sys.stdout.write("\r\n")

    def _resolv(self, path):
        options = globals.options
        client = Client(self._endpoint(), options.username, options.password)
        result = client.read("directory/user/" + path)
        if result.has_key('uuid') : return result['uuid']
    
    def _delete(self, argv):
        options = globals.options

        # Require an object as argument
        if len(argv) == 0:
            raise MissingException("You must provide a valid object identifier")

        # Validate input parameters
        if options.uuid:
            uuid = argv[0]
        else:
            uuid = self._resolv(argv[0])
            if not uuid: raise NotFoundException(uuid)

        client = Client(self._endpoint(), options.username, options.password)
        item = client.read(self._resource + "/" + uuid)

        if (prompt.confirm(prompt="Delete " + item['username'] + " ?", resp=False)) :
            client.delete(self._resource + "/" + uuid)

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
