# control.entity - Generic controller for managing comodit entities.
# coding: utf-8
#
# Copyright 2010 Guardis SPRL, Liège, Belgium.
# Authors: Laurent Eschenauer <laurent.eschenauer@guardis.com>
#
# This software cannot be used and/or distributed without prior
# authorization from Guardis.

import json, os, completions

from comodit_client.config import Config
from comodit_client.control.abstract import AbstractController
from comodit_client.util import prompt
from comodit_client.util.editor import edit_text
from comodit_client.control.doc import ActionDoc
from collections import OrderedDict


class EntityController(AbstractController):

    def __init__(self):
        super(EntityController, self).__init__()
        self._register(["list"], self._list, self._print_list_completions)
        self._register(["show"], self._show, self._print_entity_completions)
        self._register(["add"], self._add, self._print_collection_completions)
        self._register(["update"], self._update, self._print_entity_completions)
        self._register(["delete"], self._delete, self._print_entity_completions)
        self._register(["help"], self._help)
        self._default_action = self._help

        self._doc = "Generic entities handling."
        self._str_empty = "No entities to list"
        self._register_action_doc(self._list_doc())
        self._register_action_doc(self._show_doc())
        self._register_action_doc(self._add_doc())
        self._register_action_doc(self._update_doc())
        self._register_action_doc(self._delete_doc())

    def _print_list_completions(self, param_num, argv):
        self._print_collection_completions(param_num, argv)

    def _get_list_parameters(self, argv):
        return {}

    def _list(self, argv):
        parameters = self._get_list_parameters(argv)
        entities_list = self._list_entities(argv, parameters = parameters)
        if len(entities_list) == 0:
            print(self._str_empty)
        else:
            for e in sorted(entities_list, key = self._sort_key()):
                print(self._label(e))

    def _sort_key(self):
        return lambda entity : entity.identifier

    def _label(self, entity):
        return entity.label

    def _print_identifiers(self, collection, parameters = {}):
        completions.print_entity_identifiers(collection.list(parameters))

    def _print_collection_completions(self, param_num, argv):
        pass

    def _print_entity_completions(self, param_num, argv):
        pass

    def _get_show_parameters(self, argv):
        return {}

    def _show(self, argv):
        parameters = self._get_show_parameters(argv)
        res = self._get_entity(argv, parameters = parameters)

        # Display the result
        options = self._config.options
        if options.raw:
            res.show(as_json = True)
        else:
            res.show()

    def _complete_template(self, argv, template_json):
        pass

    def _add(self, argv):
        options = self._config.options

        if options.filename:
            with open(options.filename, 'r') as f:
                item = json.load(f, object_pairs_hook=OrderedDict)
        elif options.json:
            item = json.loads(options.json, object_pairs_hook=OrderedDict)
        else :
            template_json = json.load(open(os.path.join(Config()._get_templates_path(), self._template)))
            self._complete_template(argv, template_json)
            updated = edit_text(json.dumps(template_json, indent = 4))
            item = json.loads(updated, object_pairs_hook=OrderedDict)

        res = self.get_collection(argv)._new(item)
        parameters = {}
        if options.populate:
            parameters["populate"] = "true"
        if options.default:
            parameters["default"] = "true"
        if options.test:
            parameters["test"] = "true"
        if options.flavor != None:
            parameters["flavor"] = options.flavor
        res.create(parameters = parameters)
        res.show(as_json = options.raw)

    def _prune_json_update(self, json_wrapper):
        json_wrapper._del_field("uuid")
        json_wrapper._del_field("version")

    def _update(self, argv):
        # First, get entity
        res = self._get_entity(argv)
        cur_name = res.name

        # Prune entity fields (all may not be updatable)
        self._prune_json_update(res)

        options = self._config.options
        if options.filename:
            with open(options.filename, 'r') as f:
                item = json.load(f, object_pairs_hook=OrderedDict)
        elif options.json:
            item = json.loads(options.json, object_pairs_hook=OrderedDict)
        elif len(argv) > 0:
            # Edit the entity
            original = res.get_real_json(indent = 4)
            updated = edit_text(original)
            item = json.loads(updated, object_pairs_hook=OrderedDict)

        # Check if name has changed
        if item.has_key("name"):
            new_name = item["name"]
            if cur_name != new_name:
                res.rename(new_name)

        # Update entity
        res.set_json(item)
        res.update(options.force)
        res.show(as_json = options.raw)

    def _delete(self, argv):
        res = self._get_entity(argv)
        if self._config.options.force or (prompt.confirm(prompt = "Delete " + res.name + " ?", resp = False)) :
            res.delete()

    def _help(self, argv):
        self._print_doc()

    def _get_entity(self, argv, parameters = {}):
        return self.get_collection(argv).get(self._get_name_argument(argv), parameters = parameters)

    def _list_entities(self, argv, parameters = {}):
        return self.get_collection(argv).list(parameters = parameters)

    def get_collection(self, argv):
        raise NotImplementedError

    def _list_params(self):
        return ""

    def _list_doc(self):
        return ActionDoc("list", self._list_params(), """
        List available entities.""")

    def _add_params(self):
        return ""

    def _add_doc(self):
        return ActionDoc("add", self._list_params(), """
        Add a new entity.""")

    def _update_params(self):
        return ""

    def _update_doc(self):
        return ActionDoc("update", self._list_params(), """
        Update an existing entity.""")

    def _delete_params(self):
        return ""

    def _delete_doc(self):
        return ActionDoc("delete", self._list_params(), """
        Delete an existing entity.""")

    def _show_params(self):
        return ""

    def _show_doc(self):
        return ActionDoc("show", self._list_params(), """
        Show an entity.""")
