# coding: utf-8
#
# Copyright 2010 Guardis SPRL, Liège, Belgium.
#
# This software cannot be used and/or distributed without prior
# authorization from Guardis.

from __future__ import absolute_import
from comodit_client.control.abstract import AbstractController
from comodit_client.control.doc import ActionDoc
from comodit_client.control.exceptions import ArgumentException
from . import completions


class ApplicationActionController(AbstractController):

    def __init__(self):
        super(ApplicationActionController, self).__init__()
        self._doc = "Application action on deployed host."

        self._register(["impact"], self._impact, self._print_run_completions)

        self._register(["update-file"], self._update_file, self._print_file_completions)
        self._register(["restart-service"], self._restart_service, self._print_service_completions)
        self._register(["update-service"], self._update_service, self._print_service_completions)
        self._register(["enable-service"], self._enable_service, self._print_service_completions)
        self._register(["disable-service"], self._disable_service, self._print_service_completions)
        self._register(["update-package"], self._update_package, self._print_package_completions)
        self._register(["run"], self._run_action, self._print_run_completions)

        self._register(["help"], self._help)
        self._default_action = self._help

        self._register_action_doc(self._impact_doc())
        self._register_action_doc(self._update_file_doc())
        self._register_action_doc(self._restart_service_doc())
        self._register_action_doc(self._update_service_doc())
        self._register_action_doc(self._enable_service_doc())
        self._register_action_doc(self._disable_service_doc())
        self._register_action_doc(self._update_package_doc())
        self._register_action_doc(self._run_action_doc())

    def _help(self, argv):
        self._print_doc()
        
    def _get_host(self, argv):
        return self._client.hosts(argv[0], argv[1]).get(argv[2])
        
    def _run_action(self, argv):
        if len(argv) != 5:
            raise ArgumentException("Wrong number of arguments");

        host = self._get_host(argv)
        app_name = argv[3]
        handler_name = argv[4]

        host.get_application(app_name).run_handler(handler_name)

    def _print_run_completions(self, param_num, argv):
        if param_num < 4:
            self._print_host_completions(param_num, argv)
        elif len(argv) > 3 and param_num == 4:
            app = self._client.get_application(argv[0], argv[3])
            for res in app.handlers:
                completions.print_escaped_string(res.name)
        
    def _print_action_completions(self, param_num, argv):
        if param_num < 4:
            self._print_host_completions(param_num, argv)
            
    def _print_host_completions(self, param_num, argv):
        if param_num == 0:
            completions.print_entity_identifiers(self._client.organizations().list())
        elif len(argv) > 0 and param_num == 1:
            completions.print_entity_identifiers(self._client.environments(argv[0]).list())
        elif len(argv) > 1 and param_num == 2:
            completions.print_entity_identifiers(self._client.hosts(argv[0], argv[1]).list())
        elif len(argv) > 2 and param_num == 3:
            completions.print_entity_identifiers(self._client.get_host(argv[0], argv[1], argv[2]).applications())
        
    def _print_file_completions(self, param_num, argv):
        if param_num < 4:
            self._print_host_completions(param_num, argv)
        elif len(argv) > 3 and param_num == 4:
            app = self._client.get_application(argv[0], argv[3])
            for res in app.files_f:
                completions.print_escaped_string(res.name)

    def _print_service_completions(self, param_num, argv):
        if param_num < 4:
            self._print_host_completions(param_num, argv)
        elif len(argv) > 3 and param_num == 4:
            app = self._client.get_application(argv[0], argv[3])
            for res in app.services:
                completions.print_escaped_string(res.name)

    def _print_package_completions(self, param_num, argv):
        if param_num < 4:
            self._print_host_completions(param_num, argv)
        elif len(argv) > 3 and param_num == 4:
            app = self._client.get_application(argv[0], argv[3])
            for res in app.packages:
                completions.print_escaped_string(res.name)

    def _impact(self, argv):
        
        if len(argv) != 5:
            raise ArgumentException("Wrong number of arguments");

        app_name = argv[3]
        key = argv[4]
                
        application = self._client.get_application(argv[0], app_name)
        application.show_action(key)
        
    def _impact_doc(self):
        return ActionDoc("impact", "<org_name> <env_name> <host_name> <app_name> <cmd_key>", """
        get impact action.""")
        
    def _update_file(self, argv):
        if len(argv) < 4:
            raise ArgumentException("Wrong number of arguments")

        host = self._get_host(argv)
        app_name = argv[3]
        file_name = argv[4]
        host.live_update_file(app_name, file_name)

    def _update_file_doc(self):
        return ActionDoc("udpate-file", "<org_name> <env_name> <host_name> <app_name> <file_name>", """
        Updates file on given host.""")

    def _restart_service(self, argv):
        if len(argv) < 4:
            raise ArgumentException("Wrong number of arguments")

        host = self._get_host(argv)
        app_name = argv[3]
        svc_name = argv[4]
        host.live_restart_service(app_name, svc_name)

    def _restart_service_doc(self):
        return ActionDoc("restart-service", "<org_name> <env_name> <host_name> <app_name> <svc_name>", """
        Restarts service on given host.""")

    def _update_service(self, argv):
        if len(argv) < 4:
            raise ArgumentException("Wrong number of arguments")

        host = self._get_host(argv)
        app_name = argv[3]
        svc_name = argv[4]
        host.live_update_service(app_name, svc_name)

    def _update_service_doc(self):
        return ActionDoc("update-service", "<org_name> <env_name> <host_name> <app_name> <svc_name>", """
        Updates service on given host.""")
    
    def _enable_service(self, argv):
        if len(argv) < 4:
            raise ArgumentException("Wrong number of arguments")

        host = self._get_host(argv)
        app_name = argv[3]
        svc_name = argv[4]
        host.live_enable_service(app_name, svc_name)

    def _enable_service_doc(self):
        return ActionDoc("enable-service", "<org_name> <env_name> <host_name> <app_name> <svc_name>", """
        Enables service on given host.""")
    
    def _disable_service(self, argv):
        if len(argv) < 4:
            raise ArgumentException("Wrong number of arguments")

        host = self._get_host(argv)
        app_name = argv[3]
        svc_name = argv[4]
        host.live_disable_service(app_name, svc_name)

    def _disable_service_doc(self):
        return ActionDoc("disable-service", "<org_name> <env_name> <host_name> <app_name> <svc_name>", """
        Disables service on given host.""")

    def _update_package(self, argv):
        if len(argv) < 4:
            raise ArgumentException("Wrong number of arguments")

        host = self._get_host(argv)
        app_name = argv[3]
        pkg_name = argv[4]
        pkg_version = argv[5]
        host.live_update_package(app_name, pkg_name, pkg_version)

    def _update_package_doc(self):
        return ActionDoc("update-package", "<org_name> <env_name> <host_name> <app_name> <pkg_name> <pkg_version>", """
        Update package on given host.""")
   
    def _run_action_doc(self):
        return ActionDoc("run", "<org_name> <env_name> <host_name> <app_name> <cmd_key>", """
        Executes handlers associated to given key.""")
    