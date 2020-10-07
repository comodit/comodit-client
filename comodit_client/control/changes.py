# control.applications - Controller for comodit Applications entities.
# coding: utf-8
#
# Copyright 2010 Guardis SPRL, Liège, Belgium.
# Authors: Laurent Eschenauer <laurent.eschenauer@guardis.com>
#
# This software cannot be used and/or distributed without prior
# authorization from Guardis.

from __future__ import absolute_import
from __future__ import print_function

from comodit_client.control.doc import ActionDoc
from comodit_client.control.entity import EntityController
from comodit_client.control.exceptions import ArgumentException

from . import completions


class ChangeController(EntityController):

    def __init__(self):
        super(ChangeController, self).__init__()
        self._doc = "Host changes handling."

        self._unregister("add")
        self._unregister("update")

        self._register(["delete-all"], self._delete_all, self._print_collection_completions)
        self._register(["list-all"], self._list_all, self._print_collection_completions)

        self._register_action_doc(self._delete_all_doc())
        self._register_action_doc(self._list_all_doc())

        self._update_action_doc_params("show", "<org_name> <env_name> <host_name> <order_num>")
        self._update_action_doc_params("delete", "<org_name> <env_name> <host_name> <order_num>")
        self._update_action_doc_params("list", "<org_name> <env_name> <host_name>")

    def get_collection(self, argv):
        if len(argv) < 3:
            raise ArgumentException("Wrong number of arguments");
        return self._client.get_host(argv[0], argv[1], argv[2]).changes()

    def _print_collection_completions(self, param_num, argv):
        if param_num == 0:
            completions.print_identifiers(self._client.organizations())
        elif len(argv) > 0 and param_num == 1:
            completions.print_identifiers(self._client.environments(argv[0]))
        elif len(argv) > 1 and param_num == 2:
            completions.print_identifiers(self._client.hosts(argv[0], argv[1]))

    def _print_entity_completions(self, param_num, argv):
        if param_num < 3:
            self._print_collection_completions(param_num, argv)
        elif len(argv) > 2 and param_num == 3:
            changes = self._client.get_host(argv[0], argv[1], argv[2]).changes().list(show_processed = True)
            for c in changes:
                completions.print_escaped_string(c.identifier)

    def _get_name_argument(self, argv):
        if len(argv) < 4:
            raise ArgumentException("An organization, environment, host and order number must be provided");
        return argv[3]

    def _delete_all(self, argv):
        change_collection = self.get_collection(argv)
        changes = self.get_collection(argv).list(show_processed=True)
        has_change_pending = False
        for change in changes:
           if change.are_tasks_pending():
                has_change_pending = True

        if not has_change_pending:
            change_collection.clear()
        else :
            print("Be careful when deleting unfinished changes you may break some processes like orchestrations.")
            print()
            print(" "*1, "The following changes are pending :")

            change_finished = 0
            for change in changes:
                if change.are_tasks_pending():
                    print(" "*2, change.description)
                else:
                    change_finished += 1

            print()
            print(" "*1, "There are %d finished changes (successful or not)" % change_finished)
            print()

            # fixed for python2
            get_input = input
            try:
                get_input = raw_input
            except NameError:
                pass


            while True:
                try:
                    response = get_input("Do you want to delete finished changes (O)nly or delete (A)ll changes ?")
                    if response == 'O' or response == 'o':
                        change_collection.clear()
                        break
                    if response == 'A' or response == 'a':
                        change_collection.clear(parameters={"processed_only": False})
                        break
                except KeyboardInterrupt:
                    print()
                    break

    def _list_all(self, argv):
        changes = self.get_collection(argv)
        entities_list = changes.list(show_processed=True)
        if (len(entities_list) == 0):
            print("No entities to list")
        else:
            for r in entities_list:
                print(r.label)
    def _delete_all_doc(self):
        return ActionDoc("delete-all", "<org_name> <env_name> <host_name>", """
        Deletes all changes.""")

    def _list_all_doc(self):
        return ActionDoc("list-all", "<org_name> <env_name> <host_name>", """
        Lists all changes (even processed ones).""")
