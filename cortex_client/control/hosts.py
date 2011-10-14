# control.hosts - Controller for cortex Hosts resources.
# coding: utf-8
#
# Copyright 2010 Guardis SPRL, Liège, Belgium.
# Authors: Laurent Eschenauer <laurent.eschenauer@guardis.com>
#
# This software cannot be used and/or distributed without prior
# authorization from Guardis.

import json

from cortex_client.util import globals, prompt
from cortex_client.control.resource import ResourceController
from cortex_client.control.exceptions import NotFoundException, MissingException
from cortex_client.rest.client import Client
from cortex_client.rest.exceptions import ApiException

class HostsController(ResourceController):

    _resource = "hosts"
    _template = "host.json"

    def __init__(self):
        super(HostsController, self ).__init__()
        self._register(["s", "state"], self._state)
        self._register(["start"], self._start)
        self._register(["pause"], self._pause)
        self._register(["resume"], self._resume)
        self._register(["shutdown"], self._shutdown)
        self._register(["poweroff"], self._poweroff)

    def _list(self, argv):
        options = globals.options
        self._parameters = {}

        # Validate input parameters
        if options.env_uuid:
            uuid = options.env_uuid
        elif options.env_path:
            path = options.env_path
            uuid = self._resolv(path)
            if not uuid: raise NotFoundException(path)
        elif options.env and options.uuid:
            uuid = options.env
        elif options.env:
            path = options.env
            uuid = self._resolv(path)
            if not uuid: raise NotFoundException(path)
        else :
            uuid = None

        if uuid : self._parameters["environmentId"] = uuid

        super(HostsController, self)._list(argv)

    def _get_uuid(self, argv):
        if len(argv) == 0:
            raise MissingException("You must provide a valid host identifier")

        # Validate input parameters
        if globals.options.uuid:
            return argv[0]
        else:
            uuid = self._resolv(argv[0])
            if not uuid: raise NotFoundException(uuid)
            return uuid

    def _state(self, argv):
        options = globals.options

        uuid = self._get_uuid(argv)

        # Query the server
        client = Client(self._endpoint(), options.username, options.password)
        result = client.read(self._resource + "/" + uuid + "/state")

        if options.raw:
            print json.dumps(result, sort_keys=True, indent=4)
        else:
            self._renderState(result)

    def _render(self, item, detailed=False):
        if not detailed:
            print item['uuid'], item['name']
        else:
            print "Name:", item['name']
            print "UUID:", item['uuid']
            if item.has_key('description'):
                print "Description:", item['description']

    def _renderState(self, item,):
        print "State:", item['state']
        if item.has_key('cpuTime'):
            print "CPU Time:", item['cpuTime']

    def _resolv(self, path):
        options = globals.options
        client = Client(self._endpoint(), options.username, options.password)
        result = client.read("directory/organization/" + path)
        if result.has_key('uuid') : return result['uuid']

    def _apply_action(self, action, argv):
        options = globals.options

        uuid = self._get_uuid(argv)

        # Query the server
        client = Client(self._endpoint(), options.username, options.password)
        client.update(self._resource + "/" + uuid + "/" + action, decode=False)

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

        if (prompt.confirm(prompt="Delete " + item['name'] + " ?", resp=False)) :
            if(prompt.confirm(prompt="Delete VM also ?", resp=False)):
                try:
                    client.update(self._resource + "/" + uuid + "/_delete", decode=False)
                except ApiException, e:
                    if(e.code == 400):
                        print "Could not delete VM:", e.message
                    else:
                        raise e
            client.delete(self._resource + "/" + uuid)

    def _start(self, argv):
        self._apply_action("_start", argv)

    def _pause(self, argv):
        self._apply_action("_pause", argv)
        
    def _resume(self, argv):
        self._apply_action("_resume", argv)

    def _shutdown(self, argv):
        self._apply_action("_stop", argv)
        
    def _poweroff(self, argv):
        self._apply_action("_off", argv)

    def _help(self, argv):
        print '''You must provide an action to perfom on this resource.

Actions:
    list [--env <id> | --env-path <path> | --env-uuid <uuid>]
                       List all hosts, optionally within an environment
    show <id>          Show the details of a host
    state <id>         Show the state of a host
    add                Add an host
    update <id>        Update a host
    delete <id>        Delete a host
    start <id>         Start a host
    pause <id>         Pause a host
    resume <id>        Resume a host's execution
    shutdown <id>      Shutdown a host
    poweroff <id>      Power-off a host

A path may uniquely define an environment or a host. The path to a particular
environment is as follows: <organization name>/<environment name>. The path
to a particular host is as follows: <organization name>/<environment name>/
<host name>.

<id> may either be a UUID (--with-uuid option must be provided) or a path.
'''
