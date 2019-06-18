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
from comodit_client.control.settings import ApplicationContextSettingsController, \
    PlatformContextSettingsController, DistributionContextSettingsController

from . import completions
from .application_action import ApplicationActionController;

class AbstractContextController(EntityController):
    def __init__(self, unregister_update=True):
        super(AbstractContextController, self).__init__()

        # actions
        self._register(["render-file"], self._render_file, self._print_render_file_completions)
        self._register(["link"], self._get_link, self._print_render_file_completions)
        if unregister_update:
            self._unregister(["update"])

        self._update_action_doc_params("list", "<org_name> <env_name> <host_name>")
        self._update_action_doc_params("show", "<org_name> <env_name> <host_name> <name>")
        self._update_action_doc_params("add", "<org_name> <env_name> <host_name>")
        self._update_action_doc_params("delete", "<org_name> <env_name> <host_name> <name>")

        self._register_action_doc(self._render_file_doc())
        self._register_action_doc(self._get_link_doc())

    def _get_environments(self, argv):
        return self._client.environments(argv[0])

    def _get_hosts(self, argv):
        return self._client.hosts(argv[0], argv[1])

    def _get_host(self, argv):
        return self._client.get_host(argv[0], argv[1], argv[2])


class ApplicationContextController(AbstractContextController):

    _template = "application_context.json"

    def __init__(self):
        super(ApplicationContextController, self).__init__(unregister_update=False)

        # subcontroller
        self._register_subcontroller(["settings"], ApplicationContextSettingsController())
        self._register_subcontroller(["actions"], ApplicationActionController())

        # actions
        self._register(["install"], self._install, self._print_install_completions)
        self._register(["uninstall"], self._uninstall, self._print_entity_completions)

        # 'install' and 'uninstall' are aliases for 'add' and 'delete'
        self._unregister(["add", "delete"])

        self._doc = "Application contexts handling."
        self._register_action_doc(self._install_doc())
        self._register_action_doc(self._uninstall_doc())

    def get_collection(self, argv):
        if len(argv) < 3:
            raise ArgumentException("Wrong number of arguments");

        return self._client.get_host(argv[0], argv[1], argv[2]).applications()

    def _complete_template(self, argv, template_json):
        if len(argv) < 4:
            raise ArgumentException("Wrong number of arguments");

        app = self._client.get_application(argv[0], argv[3])
        template_json["application"] = app.name
        template_json["services"] = [{"name": s.name, "enabled": s.enabled} for s in app.services]
        template_json["settings"] = [{"key": p.key, "value": p.value} for p in app.parameters_f]

    def _get_name_argument(self, argv):
        if len(argv) < 4:
            raise ArgumentException("Wrong number of arguments");

        return argv[3]

    def _get_value_argument(self, argv):
        if len(argv) < 5:
            return None

        return argv[4]

    def _print_collection_completions(self, param_num, argv):
        if param_num == 0:
            completions.print_identifiers(self._client.organizations())
        elif len(argv) > 0 and param_num == 1:
            completions.print_identifiers(self._get_environments(argv))
        elif len(argv) > 1 and param_num == 2:
            completions.print_identifiers(self._get_hosts(argv))

    def _print_entity_completions(self, param_num, argv):
        if param_num < 3:
            self._print_collection_completions(param_num, argv)
        elif len(argv) > 0 and param_num == 3:
            completions.print_identifiers(self._get_host(argv).applications())

    def _print_install_completions(self, param_num, argv):
        if param_num < 3:
            self._print_collection_completions(param_num, argv)
        elif len(argv) > 0 and param_num == 3:
            completions.print_identifiers(self._client.applications(argv[0]))

    def _print_uninstall_completions(self, param_num, argv):
        if param_num < 3:
            self._print_collection_completions(param_num, argv)
        elif len(argv) > 2 and param_num == 3:
            completions.print_identifiers(self._get_host(argv).applications())

    def _print_render_file_completions(self, param_num, argv):
        if param_num < 4:
            self._print_uninstall_completions(param_num, argv)
        elif len(argv) > 3 and param_num == 4:
            completions.print_identifiers(self._client.get_application(argv[0], argv[3]).files())

    def _install(self, argv):
        self._add(argv)

    def _install_doc(self):
        return ActionDoc("install", "<org_name> <env_name> <host_name> <app_name>", """
        Install an application on host.""")

    def _uninstall(self, argv):
        self._delete(argv)

    def _uninstall_doc(self):
        return ActionDoc("uninstall", "<org_name> <env_name> <host_name> <app_name>", """
        Uninstall an application from host.""")

    def _run_action_doc(self):
        return ActionDoc("run-action", "<org_name> <env_name> <host_name> <app_name> <cmd_key>", """
        Executes handlers associated to given key.""")

    def _render_file(self, argv):
        if len(argv) != 5:
            raise ArgumentException("Wrong number of arguments");

        host = self._get_host(argv)
        app_name = argv[3]
        file_name = argv[4]

        print(host.render_app_file(app_name, file_name))

    def _render_file_doc(self):
        return ActionDoc("render-file", "<org_name> <env_name> <host_name> <app_name> <file_name>", """
        Render an application's file.""")

    def _get_link(self, argv):
        if len(argv) < 5:
            raise ArgumentException("Wrong number of arguments");

        host = self._get_host(argv)
        app_name = argv[3]
        file_name = argv[4]
        short = True if len(argv) == 6 and argv[5] == "True" else False

        print(host.get_app_link(app_name, file_name, short))

    def _get_link_doc(self):
        return ActionDoc("link", "<org_name> <env_name> <host_name> <app_name> <file_name>", """
        Prints the public URL to a rendered file.""")

class PlatformContextController(AbstractContextController):

    _template = "platform_context.json"

    def __init__(self):
        super(PlatformContextController, self).__init__()

        # subcontroller
        self._register_subcontroller(["settings"], PlatformContextSettingsController())

        self._unregister(["update", "list"])

        self._doc = "Platform contexts handling."

    def get_collection(self, argv):
        if len(argv) < 3:
            raise ArgumentException("Wrong number of arguments");

        return self._get_host(argv).platform()

    def _get_name_argument(self, argv):
        return ""

    def _print_collection_completions(self, param_num, argv):
        if param_num == 0:
            completions.print_identifiers(self._client.organizations())
        elif len(argv) > 0 and param_num == 1:
            completions.print_identifiers(self._get_environments(argv))
        elif len(argv) > 1 and param_num == 2:
            completions.print_identifiers(self._get_hosts(argv))

    def _print_entity_completions(self, param_num, argv):
        if param_num < 3:
            self._print_collection_completions(param_num, argv)

    def _print_render_file_completions(self, param_num, argv):
        if param_num < 3:
            self._print_entity_completions(param_num, argv)
        elif len(argv) > 0 and param_num == 3:
            host = self._get_host(argv)
            completions.print_identifiers(self._client.get_platform(argv[0], host.platform_name).files())

    def _render_file(self, argv):
        if len(argv) != 4:
            raise ArgumentException("Wrong number of arguments");

        host = self._get_host(argv)
        file_name = argv[3]

        print(host.render_plat_file(file_name))

    def _render_file_doc(self):
        return ActionDoc("render-file", "<org_name> <env_name> <host_name> <file_name>", """
        Render a platform's file.""")

    def _get_link(self, argv):
        if len(argv) < 4:
            raise ArgumentException("Wrong number of arguments");

        host = self._get_host(argv)
        file_name = argv[3]
        short = True if len(argv) == 5 and argv[4] == "True" else False

        print(host.get_plat_link(file_name, short))

    def _get_link_doc(self):
        return ActionDoc("link", "<org_name> <env_name> <host_name> <file_name>", """
        Prints the public URL to a rendered file.""")

class DistributionContextController(AbstractContextController):

    _template = "distribution_context.json"

    def __init__(self):
        super(DistributionContextController, self).__init__()

        # subcontroller
        self._register_subcontroller(["settings"], DistributionContextSettingsController())

        self._unregister(["update", "list"])

        self._doc = "Distribution contexts handling."

    def get_collection(self, argv):
        if len(argv) < 3:
            raise ArgumentException("Wrong number of arguments");

        return self._client.get_host(argv[0], argv[1], argv[2]).distribution()

    def _get_name_argument(self, argv):
        return ""

    def _print_collection_completions(self, param_num, argv):
        if param_num == 0:
            completions.print_identifiers(self._client.organizations())
        elif len(argv) > 0 and param_num == 1:
            completions.print_identifiers(self._get_environments(argv))
        elif len(argv) > 1 and param_num == 2:
            completions.print_identifiers(self._get_hosts(argv))

    def _print_entity_completions(self, param_num, argv):
        if param_num < 3:
            self._print_collection_completions(param_num, argv)

    def _print_render_file_completions(self, param_num, argv):
        if param_num < 3:
            self._print_entity_completions(param_num, argv)
        elif len(argv) > 0 and param_num == 3:
            host = self._get_host(argv)
            completions.print_identifiers(self._client.get_distribution(argv[0], host.distribution_name).files())

    def _render_file(self, argv):
        if len(argv) != 4:
            raise ArgumentException("Wrong number of arguments");

        host = self._get_host(argv)
        file_name = argv[3]

        print(host.render_dist_file(file_name))

    def _render_file_doc(self):
        return ActionDoc("render-file", "<org_name> <env_name> <host_name> <file_name>", """
        Render a distribution's file.""")

    def _get_link(self, argv):
        if len(argv) < 4:
            raise ArgumentException("Wrong number of arguments");

        host = self._get_host(argv)
        file_name = argv[3]
        short = True if len(argv) == 5 and argv[4] == "True" else False

        print(host.get_dist_link(file_name, short))

    def _get_link_doc(self):
        return ActionDoc("link", "<org_name> <env_name> <host_name> <file_name>", """
        Prints the public URL to a rendered file.""")

