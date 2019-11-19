# coding: utf-8

from __future__ import absolute_import
import json

from comodit_client.control.entity import EntityController
from comodit_client.control.exceptions import ArgumentException
from comodit_client.control.doc import ActionDoc

from . import completions


class OrganizationGroupsController(EntityController):

    def __init__(self):
        super(OrganizationGroupsController, self).__init__()

        # Unregister unsupported actions
        self._unregister(["add", "delete"])

        self._doc = "Groups handling."
        self._register(["tree"], self._tree, self._print_list_completions)
        self._register_action_doc(self._tree_doc())


    def get_collection(self, argv):
        if len(argv) < 1:
            raise ArgumentException("Wrong number of arguments");
        return self._client.get_organization(argv[0]).groups()

    def _print_collection_completions(self, param_num, argv):
        if param_num == 0:
            completions.print_identifiers(self._client.organizations())

    def _print_entity_completions(self, param_num, argv):
        if param_num == 0:
            self._print_collection_completions(param_num, argv)
        elif len(argv) > 0 and param_num == 1:
            completions.print_identifiers(self.get_collection(argv))

    def _get_name_argument(self, argv):
        if len(argv) < 2:
            raise ArgumentException("An organization name and a group name must be provided")
        return argv[1]

    def _tree(self, argv):
        res = self._client.get_organization(argv[0]).groupsTree()
        if self._config.options.raw:
            print(json.dumps(res.get_json(), indent=4))
        else:
            res.show()

    def _tree_doc(self):
        return ActionDoc("tree", "<org_name>  ", """
        Get a tree of each groups in organization.""")


class EnvironmentGroupsController(EntityController):
    def __init__(self):
        super(EnvironmentGroupsController, self).__init__()

        # Unregister unsupported actions
        self._unregister(["add", "delete"])

        self._doc = "Groups handling."
        self._register(["tree"], self._tree, self._print_list_completions)
        self._register_action_doc(self._tree_doc())


    def get_collection(self, argv):
        if len(argv) < 2:
            raise ArgumentException("Wrong number of arguments");
        # return self._client.get_organization(argv[0]).groups()
        return self._client.get_environment(argv[0], argv[1]).groups()

    def _print_collection_completions(self, param_num, argv):
        if param_num == 0:
            completions.print_identifiers(self._client.organizations())
        if param_num == 1:
            completions.print_identifiers(self._client.get_organization(argv[0]).environments())

    def _print_entity_completions(self, param_num, argv):
        if param_num < 2:
            self._print_collection_completions(param_num, argv)
        elif len(argv) > 1 and param_num == 2:
            completions.print_identifiers(self._client.get_environment(argv[0], argv[1]).groups())

    def _get_name_argument(self, argv):
        if len(argv) < 3:
            raise ArgumentException("An organization name and ank environment name and a group name must be provided")
        return argv[2]

    def _tree(self, argv):
        res = self._client.get_environment(argv[0], argv[1]).groupsTree()
        if self._config.options.raw:
            print(json.dumps(res.get_json(), indent=4))
        else:
            res.show()

    def _tree_doc(self):
        return ActionDoc("tree", "<org_name>  ", """
        Get a tree of each groups in environment.""")

class HostGroupsController(EntityController):
    def __init__(self):
        super(HostGroupsController, self).__init__()

        # Unregister unsupported actions
        self._unregister(["add", "delete"])
        self._doc = "Groups handling."
        self._register(["tree"], self._tree, self._print_list_completions)
        self._register_action_doc(self._tree_doc())

    def get_collection(self, argv):
        if len(argv) < 3:
            raise ArgumentException("Wrong number of arguments");
        # return self._client.get_organization(argv[0]).groups()
        return self._client.get_host(argv[0], argv[1], argv[2]).groups()

    def _print_collection_completions(self, param_num, argv):
        if param_num == 0:
            completions.print_identifiers(self._client.organizations())
        elif param_num == 1:
            completions.print_identifiers(self._client.get_organization(argv[0]).environments())
        elif param_num == 2:
            completions.print_identifiers(self._client.get_environment(argv[0], argv[1]).hosts())

    def _print_entity_completions(self, param_num, argv):
        if param_num < 3:
            self._print_collection_completions(param_num, argv)
        elif len(argv) > 1 and param_num == 3:
            completions.print_identifiers(self._client.get_host(argv[0], argv[1], argv[2]).groups())

    def _get_name_argument(self, argv):
        if len(argv) < 4:
            raise ArgumentException("An organization name and ank environment name and host name and a group name must be provided")
        return argv[3]

    def _tree(self, argv):
        res = self._client.get_host(argv[0], argv[1], argv[2]).groupsTree()
        if self._config.options.raw:
            print(json.dumps(res.get_json(), indent=4))
        else:
            res.show()

    def _tree_doc(self):
        return ActionDoc("tree", "<org_name>  ", """
        Get a tree of each groups in host.""")
