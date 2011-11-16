# control.resource - Generic controller for managing cortex resources.
# coding: utf-8
#
# Copyright 2010 Guardis SPRL, Liège, Belgium.
# Authors: Laurent Eschenauer <laurent.eschenauer@guardis.com>
#
# This software cannot be used and/or distributed without prior
# authorization from Guardis.

import json, os

from cortex_client.config import Config
from cortex_client.control.abstract import AbstractController
from cortex_client.util import globals, prompt
from cortex_client.util.editor import edit_text
from cortex_client.control.exceptions import MissingException


class ResourceController(AbstractController):

    def __init__(self):
        super(ResourceController, self).__init__()
        self._register(["list"], self._list, self._print_list_completions)
        self._register(["show"], self._show, self._print_show_completions)
        self._register(["add"], self._add, self._print_add_completions)
        self._register(["update"], self._update, self._print_update_completions)
        self._register(["delete"], self._delete, self._print_delete_completions)
        self._register(["help"], self._help, self._print_help_completions)
        self._default_action = self._help

    def _print_list_completions(self, param_num, argv):
        pass

    def _list(self, argv):
        resources_list = self._get_resources(argv)
        if(len(resources_list) == 0):
            print "No resources to list"
        else:
            for r in resources_list:
                print r.get_uuid(), r.get_identifier()

    def _print_identifiers(self, argv):
        resources_list = self._get_resources(argv)

        if len(argv) > 0:
            # Check if completions are available
            id = argv[0]
            for res in resources_list:
                if id == res.get_identifier():
                    return

        for r in resources_list:
            print r.get_identifier()

    def _print_show_completions(self, param_num, argv):
        if(param_num == 0):
            self._print_identifiers(argv)

    def _show(self, argv):
        res = self._get_resource(argv)

        # Display the result
        options = globals.options
        if options.raw:
            res.show(as_json = True)
        else:
            res.show()

    def _print_add_completions(self, param_num, argv):
        pass

    def _add(self, argv):
        options = globals.options

        if options.filename:
            with open(options.filename, 'r') as f:
                item = json.load(f)
                res = self.get_collection()._new_resource(item)
        elif options.json:
            item = json.loads(options.json)
            res = self.get_collection()._new_resource(item)
        else :
            template = open(os.path.join(Config().templates_path, self._template)).read()
            #template = "# To abort the request; just exit your editor without saving this file.\n\n" + template
            updated = edit_text(template)
            #updated = re.sub(r'#.*$', "", updated)
            res = self.get_collection()._new_resource(json.loads(updated))

        res.create()
        res.show(as_json = options.raw)

    def _print_update_completions(self, param_num, argv):
        pass

    def _update(self, argv):
        options = globals.options

        if options.filename:
            with open(options.filename, 'r') as f:
                item = json.load(f)
                res = self._new_resource(item)
        elif options.json:
            item = json.loads(options.json)
            res = self._new_resource(item)
        elif len(argv) > 0:
            res = self._get_resource(argv)
            # Edit the resource
            original = json.dumps(res.get_json(), sort_keys = True, indent = 4)
            #original = "# To abort the request; just exit your editor without saving this file.\n\n" + original
            updated = edit_text(original)
            #updated = re.sub(r'#.*$', "", updated)
            res.set_json(json.loads(updated))

        res.commit(options.force)
        res.show(as_json = options.raw)

    def _print_delete_completions(self, param_num, argv):
        self._print_identifiers(argv)

    def _delete(self, argv):
        res = self._get_resource(argv)
        if (prompt.confirm(prompt = "Delete " + res.get_name() + " ?", resp = False)) :
            res.delete()

    def _print_help_completions(self, param_num, argv):
        pass

    def _help(self, argv):
        print "Oops, this piece is missing some documentation"

    def _get_resource(self, argv):
        if len(argv) == 0:
            raise MissingException("You must provide a valid host identifier")

        # Validate input parameters
        if(globals.options.uuid):
            return self.get_collection().get_resource(argv[0])
        else:
            return self.get_collection().get_resource_from_path(argv[0])

    def _get_resources(self, argv, parameters = {}):
        return self.get_collection().get_resources(parameters)

    def get_collection(self):
        raise NotImplementedError
