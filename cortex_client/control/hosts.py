# control.hosts - Controller for cortex Hosts resources.
# coding: utf-8
#
# Copyright 2010 Guardis SPRL, Liège, Belgium.
# Authors: Laurent Eschenauer <laurent.eschenauer@guardis.com>
#
# This software cannot be used and/or distributed without prior
# authorization from Guardis.

from cortex_client.util import globals, prompt
from cortex_client.control.resource import ResourceController
from cortex_client.control.exceptions import NotFoundException

class HostsController(ResourceController):

    _template = "host.json"

    def __init__(self):
        super(HostsController, self ).__init__()
        self._register(["s", "state"], self._state)
        self._register(["provision"], self._provision)
        self._register(["start"], self._start)
        self._register(["pause"], self._pause)
        self._register(["resume"], self._resume)
        self._register(["shutdown"], self._shutdown)
        self._register(["poweroff"], self._poweroff)

    def get_collection(self):
        return self._api.get_host_collection()

    def _get_resources(self, argv):
        options = globals.options
        parameters = {}

        # Validate input parameters
        env_uuid = None
        if options.env_uuid:
            env_uuid = options.env_uuid
        elif options.env_path:
            path = options.env_path
            env_uuid = self._api.get_directory().get_environment_uuid_from_path(path)
            if not env_uuid: raise NotFoundException(path)
        elif options.env and options.uuid:
            env_uuid = options.env
        elif options.env:
            path = options.env
            env_uuid = self._api.get_directory().get_environment_uuid_from_path(path)
            if not env_uuid: raise NotFoundException(path)

        if(env_uuid):
            parameters["environmentId"] = env_uuid

        return super(HostsController, self)._get_resources(argv, parameters)

    def _state(self, argv):
        options = globals.options
        host = self._get_resource(argv)

        if options.raw:
            host.get_state().show(as_json = True)
        else:
            host.get_state().show()

    def _delete(self, argv):
        host = self._get_resource(argv)

        if (prompt.confirm(prompt="Delete " + host.get_name() + " ?", resp=False)) :
            delete_vm = prompt.confirm(prompt="Delete VM also ?", resp=False)
            host.delete(delete_vm)

    def _provision(self, argv):
        host = self._get_resource(argv)
        host.provision()

    def _start(self, argv):
        host = self._get_resource(argv)
        host.start()

    def _pause(self, argv):
        host = self._get_resource(argv)
        host.pause()

    def _resume(self, argv):
        host = self._get_resource(argv)
        host.resume()

    def _shutdown(self, argv):
        host = self._get_resource(argv)
        host.shutdown()

    def _poweroff(self, argv):
        host = self._get_resource(argv)
        host.poweroff()

    def _help(self, argv):
        print '''You must provide an action to perform on this resource.

Actions:
    list [--env <id> | --env-path <path> | --env-uuid <uuid>]
                       List all hosts, optionally within an environment
    show <id>          Show the details of a host
    state <id>         Show the state of a host
    add                Add an host
    update <id>        Update a host
    delete <id>        Delete a host
    provision <id>     Provision a host
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
