# coding: utf-8

from __future__ import print_function

import json

from comodit_client.api.platform import Image
from comodit_client.api.settings import SimpleSetting
from comodit_client.control import completions
from comodit_client.control.doc import ActionDoc
from comodit_client.control.entity import EntityController
from comodit_client.control.exceptions import ArgumentException
from comodit_client.control.json_update import JsonUpdater


class InstancesController(EntityController):

    def __init__(self):
        super(InstancesController, self).__init__()

        # actions
        self._register(["start"], self._start, self._print_entity_completions)
        self._register(["pause"], self._pause, self._print_entity_completions)
        self._register(["resume"], self._resume, self._print_entity_completions)
        self._register(["shutdown"], self._shutdown, self._print_entity_completions)
        self._register(["poweroff"], self._poweroff, self._print_entity_completions)
        self._register(["forget"], self._forget, self._print_entity_completions)
        self._register(["properties"], self._properties, self._print_entity_completions)
        self._register(["show_file"], self._show_file, self._print_entity_completions)
        self._register(["get_status"], self._get_status, self._print_entity_completions)
        self._register(["create_image"], self._create_image, self._print_entity_completions)

        # Unregister unsupported actions
        self._unregister(["update", "list", "add"])

        self._doc = "Host instances handling."
        self._update_action_doc_params("delete", "<org_name>  <env_name> <host_name>")
        self._update_action_doc_params("show", "<org_name>  <env_name> <host_name>")
        self._register_action_doc(self._start_doc())
        self._register_action_doc(self._pause_doc())
        self._register_action_doc(self._resume_doc())
        self._register_action_doc(self._shutdown_doc())
        self._register_action_doc(self._poweroff_doc())
        self._register_action_doc(self._forget_doc())
        self._register_action_doc(self._properties_doc())
        self._register_action_doc(self._show_file_doc())
        self._register_action_doc(self._get_status_doc())
        self._register_action_doc(self._create_image_doc())


    def get_collection(self, argv):
        if len(argv) < 3:
            raise ArgumentException("Wrong number of arguments");
        return self._client.get_host(argv[0], argv[1], argv[2]).instance()

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

    def _get_name_argument(self, argv):
        return ""

    def _get_value_argument(self, argv):
        return None

    def _properties(self, argv):
        instance = self._get_entity(argv)
        options = self._config.options
        if options.raw:
            print(json.dumps(instance._get_field("properties"), indent = 4))
        else:
            for p in instance.properties:
                p.show()

    def _properties_doc(self):
        return ActionDoc("properties", "<org_name>  <env_name> <host_name>", """
        Show properties of a given host instance.""")

    def _delete(self, argv):
        instance = self._get_entity(argv)
        instance.delete()

    def _delete_doc(self):
        return ActionDoc("delete", "<org_name>  <env_name> <host_name>", """
        Delete a host instance.""")

    def _start(self, argv):
        instance = self._get_entity(argv)
        instance.start()

    def _start_doc(self):
        return ActionDoc("start", "<org_name>  <env_name> <host_name>", """
        Start a host instance.""")

    def _pause(self, argv):
        instance = self._get_entity(argv)
        instance.pause()

    def _pause_doc(self):
        return ActionDoc("pause", "<org_name>  <env_name> <host_name>", """
        Pause a host instance.""")

    def _resume(self, argv):
        instance = self._get_entity(argv)
        instance.resume()

    def _resume_doc(self):
        return ActionDoc("resume", "<org_name>  <env_name> <host_name>", """
        Resume a host instance.""")

    def _shutdown(self, argv):
        instance = self._get_entity(argv)
        instance.shutdown()

    def _shutdown_doc(self):
        return ActionDoc("shutdown", "<org_name>  <env_name> <host_name>", """
        Shutdown a host instance.""")

    def _poweroff(self, argv):
        instance = self._get_entity(argv)
        instance.poweroff()

    def _poweroff_doc(self):
        return ActionDoc("poweroff", "<org_name>  <env_name> <host_name>", """
        Power-off a host instance.""")

    def _forget(self, argv):
        instance = self._get_entity(argv)
        instance.forget()

    def _forget_doc(self):
        return ActionDoc("forget", "<org_name>  <env_name> <host_name>", """
        Forgets a host instance.""")

    def _show_file(self, argv):
        if len(argv) < 4:
            raise ArgumentException("Wrong number of arguments");

        instance = self._get_entity(argv)
        print(instance.get_file_content(argv[3]).read(), end=' ')

    def _show_file_doc(self):
        return ActionDoc("show_file", "<org_name>  <env_name> <host_name> <path>", """
        Show a host's file content.""")

    def _get_status(self, argv):
        if len(argv) < 5:
            raise ArgumentException("Wrong number of arguments");

        instance = self._get_entity(argv)
        print(instance.get_status(argv[3], argv[4]), end=' ')

    def _get_status_doc(self):
        return ActionDoc("get_status", "<org_name>  <env_name> <host_name> <collection> <sensor>", """
        Show a host's file content.""")

    def _create_image(self, argv):
        image = Image()
        image.create_distribution = False

        host = self._client.get_host(argv[0], argv[1], argv[2])
        platform = self._client.get_platform(argv[0], host.platform_name)
        image.settings = [ self._build_setting(param) for param in platform.image_parameters() ]

        updater = JsonUpdater(self._config.options, ignore_not_modified=True)
        updated_json = updater.update(image)
        image.set_json(updated_json)

        instance = self._get_entity(argv)
        instance.create_image(image)

    def _build_setting(self, parameter):
        setting = SimpleSetting(None)
        setting.key = parameter.key
        setting.value = parameter.value
        return setting

    def _create_image_doc(self):
        return ActionDoc("create_image", "<org_name>  <env_name> <host_name>", """
        Creates an image from given host's instance.""")
