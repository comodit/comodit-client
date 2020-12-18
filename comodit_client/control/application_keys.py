# control.environments - Controller for comodit Environments entities.
# coding: utf-8
#
# Copyright 2010 Guardis SPRL, Liège, Belgium.
# Authors: Laurent Eschenauer <laurent.eschenauer@guardis.com>
#
# This software cannot be used and/or distributed without prior
# authorization from Guardis.

from comodit_client.control.organization_entity import OrganizationEntityController

class ApplicationKeysController(OrganizationEntityController):

    _template = "application_key.json"

    def __init__(self):
        super(ApplicationKeysController, self).__init__()
        self._doc = "Application keys handling."
        self._register(["reset"], self._reset, self._print_entity_completions)
        self._unregister("clone")

    def _get_collection(self, org_name):
        print("_get_collection")
        return self._client.application_keys(org_name)

    def _reset(self, argv):
        app_key = self._client.get_application_key(argv[0], argv[1])
        app_key = app_key.reset()
        app_key.show()

    def _print_reset(self, param_num, argv):
        if param_num == 0:
            completions.print_entity_identifiers(self._client.organizations().list())
        elif len(argv) > 0 and param_num == 1:
            completions.print_entity_identifiers(self._client.application_keys(argv[0]).list())


    def _prune_json_update(self, json_wrapper):
        super(ApplicationKeysController, self)._prune_json_update(json_wrapper)
        json_wrapper._del_field("token")
        json_wrapper._del_field("creator")
        json_wrapper._del_field("organization")
