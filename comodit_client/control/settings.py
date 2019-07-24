# coding: utf-8

from __future__ import print_function
from __future__ import absolute_import
from builtins import str
from builtins import object
from . import completions
import json

from comodit_client.control.entity import EntityController
from comodit_client.control.exceptions import ArgumentException, ControllerException
from comodit_client.control.doc import ActionDoc
from comodit_client.control.json_update import JsonUpdater
from comodit_client.util.json_wrapper import JsonWrapper
from comodit_client.util import prompt
from comodit_client.api.settings import SimpleSetting, LinkSetting, PropertySetting

class HostAbstractSettingsController(EntityController):

    _template = "setting.json"

    def __init__(self):
        super(HostAbstractSettingsController, self).__init__()

        self._doc = "Settings handling."
        self._update_action_doc_params("list", "<org_name> <env_name> <host_name>")
        self._update_action_doc_params("add", "<org_name> <env_name> <host_name>")
        self._update_action_doc_params("delete", "<org_name> <env_name> <host_name> <setting_name>")
        self._update_action_doc_params("update", "<org_name> <env_name> <host_name> <setting_name>")
        self._update_action_doc_params("show", "<org_name> <env_name> <host_name> <setting_name>")

        self._register(["change"], self._change, self._print_list_completions)
        self._register_action_doc(self._change_doc())

        self._register(["list-secret"], self._list_secret, self._print_list_completions)
        self._register_action_doc(self._list_secret_doc())
        self._register(["list-non-secret"], self._list_non_secret, self._print_list_completions)
        self._register_action_doc(self._list_non_secret_doc())

    def _get_name_argument(self, argv):
        if len(argv) < 4:
            raise ArgumentException("An organization, an environment, a host and a setting name must be provided");

        return argv[3]

    def _get_value_argument(self, argv):
        if len(argv) < 5:
            return None

        return argv[4]

    def get_collection(self, argv):
        if len(argv) < 3:
            raise ArgumentException("An organization, an environment and a host must be provided");

        host = self._client.hosts(argv[0], argv[1]).get(argv[2])
        return self._get_settings(host, argv)

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
            host = self._client.get_host(argv[0], argv[1], argv[2])
            completions.print_identifiers(self._get_settings(host, argv))

    def _change(self, argv):
        settings = self.get_collection(argv)
        handler = ChangeHandler(self._config)
        handler.change(settings)

    def _change_doc(self):
        return ActionDoc("change", self._list_params(), """
        Add, update or delete Settings.""")

    def _list_secret(self, argv):
        parameters = {}
        parameters["secret_only"] = True

        self._list(argv, parameters)

    def _list_non_secret(self, argv):
        parameters = {}
        parameters["no_secret"] = True
        
        self._list(argv, parameters)

    def _list_secret_doc(self):
        return ActionDoc("list_secret", "<org_name>", """
        List secret setting.""")
    
    def _list_non_secret_doc(self):
        return ActionDoc("list_non_secret", "<org_name>", """
        List non secret setting.""")

class PlatformContextSettingsController(HostAbstractSettingsController):

    def __init__(self):
        super(PlatformContextSettingsController, self).__init__()

    def _get_settings(self, host, argv):
        return host.get_platform().settings()


class DistributionContextSettingsController(HostAbstractSettingsController):

    def __init__(self):
        super(DistributionContextSettingsController, self).__init__()

    def _get_settings(self, host, argv):
        return host.get_distribution().settings()


class ApplicationContextSettingsController(EntityController):

    _template = "setting.json"

    def __init__(self):
        super(ApplicationContextSettingsController, self).__init__()

        self._doc = "Settings handling."

        self._update_action_doc_params("list", "<org_name> <env_name> <host_name> <app_name>")
        self._update_action_doc_params("add", "<org_name> <env_name> <host_name> <app_name>")
        self._update_action_doc_params("delete", "<org_name> <env_name> <host_name> <app_name> <setting_name>")
        self._update_action_doc_params("update", "<org_name> <env_name> <host_name> <app_name> <setting_name>")
        self._update_action_doc_params("show", "<org_name> <env_name> <host_name> <app_name> <setting_name>")

        self._register(["change"], self._change, self._print_list_completions)
        self._register_action_doc(self._change_doc())

        self._register(["list-secret"], self._list_secret, self._print_list_completions)
        self._register_action_doc(self._list_secret_doc())
        self._register(["list-non-secret"], self._list_non_secret, self._print_list_completions)
        self._register_action_doc(self._list_non_secret_doc())

    def _get_name_argument(self, argv):
        if len(argv) < 5:
            raise ArgumentException("An organization, an environment, a host, an application and a setting name must be provided");

        return argv[4]

    def _get_value_argument(self, argv):
        if len(argv) < 6:
            return None

        return argv[5]

    def get_collection(self, argv):
        if len(argv) < 4:
            raise ArgumentException("An organization, an environment, a host and an application name must be provided");

        return self._client.get_host(argv[0], argv[1], argv[2]).get_application(argv[3]).settings()

    def _print_collection_completions(self, param_num, argv):
        if param_num == 0:
            completions.print_identifiers(self._client.organizations())
        elif len(argv) > 0 and param_num == 1:
            completions.print_identifiers(self._client.environments(argv[0]))
        elif len(argv) > 1 and param_num == 2:
            completions.print_identifiers(self._client.hosts(argv[0], argv[1]))
        elif len(argv) > 2 and param_num == 3:
            host = self._client.get_host(argv[0], argv[1], argv[2])
            completions.print_escaped_strings(host.application_names)

    def _print_entity_completions(self, param_num, argv):
        if param_num < 4:
            self._print_collection_completions(param_num, argv)
        elif len(argv) > 3 and param_num == 4:
            completions.print_identifiers(self._client.get_host(argv[0], argv[1], argv[2]).get_application(argv[3]))

    def _change(self, argv):
        settings = self.get_collection(argv)
        handler = ChangeHandler(self._config)
        handler.change(settings)

    def _change_doc(self):
        return ActionDoc("change", self._list_params(), """
        Add, update or delete Settings.""")

    def _list_secret(self, argv):
        parameters = {}
        parameters["secret_only"] = True

        self._list(argv, parameters)

    def _list_non_secret(self, argv):
        parameters = {}
        parameters["no_secret"] = True
        
        self._list(argv, parameters)

    def _list_secret_doc(self):
        return ActionDoc("list_secret", "<org_name>", """
        List secret setting.""")
    
    def _list_non_secret_doc(self):
        return ActionDoc("list_non_secret", "<org_name>", """
        List non secret setting.""")


class HostSettingsController(EntityController):

    _template = "setting.json"

    def __init__(self):
        super(HostSettingsController, self).__init__()

        self._doc = "Settings handling."
        self._update_action_doc_params("list", "<org_name> <env_name> <host_name>")
        self._update_action_doc_params("add", "<org_name> <env_name> <host_name>")
        self._update_action_doc_params("delete", "<org_name> <env_name> <host_name> <setting_name>")
        self._update_action_doc_params("update", "<org_name> <env_name> <host_name> <setting_name>")
        self._update_action_doc_params("show", "<org_name> <env_name> <host_name> <setting_name>")

        self._register(["change"], self._change, self._print_list_completions)
        self._register_action_doc(self._change_doc())

        self._register(["impact"], self._impact, self._print_entity_completions)
        self._register_action_doc(self._impact_doc())

        self._register(["list-secret"], self._list_secret, self._print_list_completions)
        self._register_action_doc(self._list_secret_doc())
        self._register(["list-non-secret"], self._list_non_secret, self._print_list_completions)
        self._register_action_doc(self._list_non_secret_doc())

    def _get_name_argument(self, argv):
        if len(argv) < 4:
            raise ArgumentException("An organization, an environment, a host and a setting name must be provided");

        return argv[3]

    def _get_value_argument(self, argv):
        if len(argv) < 5:
            return None

        return argv[4]

    def get_collection(self, argv):
        if len(argv) < 3:
            raise ArgumentException("An organization, an environment and a host name must be provided");

        return self._client.get_host(argv[0], argv[1], argv[2]).settings()

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
            completions.print_identifiers(self._client.get_host(argv[0], argv[1], argv[2]).settings())

    def _change(self, argv):
        settings = self.get_collection(argv)
        handler = ChangeHandler(self._config)
        handler.change(settings)

    def _change_doc(self):
        return ActionDoc("change", self._list_params(), """
        Add, update or delete Settings.""")

    def _impact(self, argv):
        res = self._client.get_host(argv[0], argv[1], argv[2]).impact(argv[3])
        if self._config.options.raw:
            print(json.dumps(res.get_json(), indent=4))            
        else:
            res.show()        
    
    def _impact_doc(self):
        return ActionDoc("impact", "<org_name> <env_name> <host_name> <setting_name>", """
        Impact analysis if setting change.""")

    def _list_secret(self, argv):
        parameters = {}
        parameters["secret_only"] = True

        self._list(argv, parameters)

    def _list_non_secret(self, argv):
        parameters = {}
        parameters["no_secret"] = True
        
        self._list(argv, parameters)

    def _list_secret_doc(self):
        return ActionDoc("list_secret", "<org_name>", """
        List secret setting.""")
    
    def _list_non_secret_doc(self):
        return ActionDoc("list_non_secret", "<org_name>", """
        List non secret setting.""")


class EnvironmentSettingsController(EntityController):

    _template = "setting.json"

    def __init__(self):
        super(EnvironmentSettingsController, self).__init__()

        self._doc = "Settings handling."
        self._update_action_doc_params("list", "<org_name> <env_name>")
        self._update_action_doc_params("add", "<org_name> <env_name>")
        self._update_action_doc_params("delete", "<org_name> <env_name> <setting_name>")
        self._update_action_doc_params("update", "<org_name> <env_name> <setting_name>")
        self._update_action_doc_params("show", "<org_name> <env_name> <setting_name>")

        self._register(["change"], self._change, self._print_list_completions)
        self._register_action_doc(self._change_doc())

        self._register(["impact"], self._impact, self._print_entity_completions)
        self._register_action_doc(self._impact_doc())

        self._register(["list-secret"], self._list_secret, self._print_list_completions)
        self._register_action_doc(self._list_secret_doc())
        self._register(["list-non-secret"], self._list_non_secret, self._print_list_completions)
        self._register_action_doc(self._list_non_secret_doc())

    def _get_name_argument(self, argv):
        if len(argv) < 3:
            raise ArgumentException("An organization, an environment and a setting name must be provided");

        return argv[2]

    def _get_value_argument(self, argv):
        if len(argv) < 4:
            return None

        return argv[3]

    def get_collection(self, argv):
        if len(argv) < 2:
            raise ArgumentException("An organization and an environment must be provided");

        return self._client.get_environment(argv[0], argv[1]).settings()

    def _print_collection_completions(self, param_num, argv):
        if param_num == 0:
            completions.print_identifiers(self._client.organizations())
        elif len(argv) > 0 and param_num == 1:
            completions.print_identifiers(self._client.environments(argv[0]))

    def _print_entity_completions(self, param_num, argv):
        if param_num < 2:
            self._print_collection_completions(param_num, argv)
        elif len(argv) > 1 and param_num == 2:
            completions.print_identifiers(self._client.get_environment(argv[0], argv[1]).settings())

    def _change(self, argv):
        settings = self.get_collection(argv)
        handler = ChangeHandler(self._config)
        handler.change(settings)

    def _change_doc(self):
        return ActionDoc("change", self._list_params(), """
        Add, update or delete Settings.""")

    def _impact(self, argv):
        res = self._client.get_environment(argv[0], argv[1]).impact(argv[2])
        if self._config.options.raw:
            print(json.dumps(res.get_json(), indent=4))            
        else:
            res.show()        
    
    def _impact_doc(self):
        return ActionDoc("impact", "<org_name> <env_name> <setting_name>", """
        Impact analysis if setting change.""")

    def _list_secret(self, argv):
        parameters = {}
        parameters["secret_only"] = True

        self._list(argv, parameters)

    def _list_non_secret(self, argv):
        parameters = {}
        parameters["no_secret"] = True
        
        self._list(argv, parameters)

    def _list_secret_doc(self):
        return ActionDoc("list_secret", "<org_name>", """
        List secret setting.""")
    
    def _list_non_secret_doc(self):
        return ActionDoc("list_non_secret", "<org_name>", """
        List non secret setting.""")



class DistributionSettingsController(EntityController):

    _template = "setting.json"

    def __init__(self):
        super(DistributionSettingsController, self).__init__()

        self._doc = "Settings handling."
        self._update_action_doc_params("list", "<org_name> <dist_name>")
        self._update_action_doc_params("add", "<org_name> <dist_name>")
        self._update_action_doc_params("delete", "<org_name> <dist_name> <setting_name>")
        self._update_action_doc_params("update", "<org_name> <dist_name> <setting_name>")
        self._update_action_doc_params("show", "<org_name> <dist_name> <setting_name>")

        self._register(["change"], self._change, self._print_list_completions)
        self._register_action_doc(self._change_doc())

        self._register(["list-secret"], self._list_secret, self._print_list_completions)
        self._register_action_doc(self._list_secret_doc())
        self._register(["list-non-secret"], self._list_non_secret, self._print_list_completions)
        self._register_action_doc(self._list_non_secret_doc())

    def _get_name_argument(self, argv):
        if len(argv) < 3:
            raise ArgumentException("An organization, a distribution and a setting name must be provided");

        return argv[2]

    def _get_value_argument(self, argv):
        if len(argv) < 4:
            return None

        return argv[3]

    def get_collection(self, argv):
        if len(argv) < 2:
            raise ArgumentException("An organization and a distribution must be provided");

        return self._client.get_distribution(argv[0], argv[1]).settings()

    def _print_collection_completions(self, param_num, argv):
        if param_num == 0:
            completions.print_identifiers(self._client.organizations())
        elif len(argv) > 0 and param_num == 1:
            completions.print_identifiers(self._client.distributions(argv[0]))

    def _print_entity_completions(self, param_num, argv):
        if param_num < 2:
            self._print_collection_completions(param_num, argv)
        elif len(argv) > 1 and param_num == 2:
            completions.print_identifiers(self._client.get_distribution(argv[0], argv[1]).settings())

    def _change(self, argv):
        settings = self.get_collection(argv)
        handler = ChangeHandler(self._config)
        handler.change(settings)

    def _change_doc(self):
        return ActionDoc("change", self._list_params(), """
        Add, update or delete Settings.""")

    def _list_secret(self, argv):
        parameters = {}
        parameters["secret_only"] = True

        self._list(argv, parameters)

    def _list_non_secret(self, argv):
        parameters = {}
        parameters["no_secret"] = True
        
        self._list(argv, parameters)

    def _list_secret_doc(self):
        return ActionDoc("list_secret", "<org_name>", """
        List secret setting.""")
    
    def _list_non_secret_doc(self):
        return ActionDoc("list_non_secret", "<org_name>", """
        List non secret setting.""")


class PlatformSettingsController(EntityController):

    _template = "setting.json"

    def __init__(self):
        super(PlatformSettingsController, self).__init__()

        self._doc = "Settings handling."
        self._update_action_doc_params("list", "<org_name> <plat_name>")
        self._update_action_doc_params("add", "<org_name> <plat_name>")
        self._update_action_doc_params("delete", "<org_name> <plat_name> <setting_name>")
        self._update_action_doc_params("update", "<org_name> <plat_name> <setting_name>")
        self._update_action_doc_params("show", "<org_name> <plat_name> <setting_name>")

        self._register(["change"], self._change, self._print_list_completions)
        self._register_action_doc(self._change_doc())

        self._register(["list-secret"], self._list_secret, self._print_list_completions)
        self._register_action_doc(self._list_secret_doc())
        self._register(["list-non-secret"], self._list_non_secret, self._print_list_completions)
        self._register_action_doc(self._list_non_secret_doc())

    def _get_name_argument(self, argv):
        if len(argv) < 3:
            raise ArgumentException("An organization, a platform and a setting name must be provided");

        return argv[2]

    def _get_value_argument(self, argv):
        if len(argv) < 4:
            return None

        return argv[3]

    def get_collection(self, argv):
        if len(argv) < 2:
            raise ArgumentException("An organization and a platform must be provided");

        return self._client.get_platform(argv[0], argv[1]).settings()

    def _print_collection_completions(self, param_num, argv):
        if param_num == 0:
            completions.print_identifiers(self._client.organizations())
        elif len(argv) > 0 and param_num == 1:
            completions.print_identifiers(self._client.platforms(argv[0]))

    def _print_entity_completions(self, param_num, argv):
        if param_num < 2:
            self._print_collection_completions(param_num, argv)
        elif len(argv) > 1 and param_num == 2:
            completions.print_identifiers(self._client.get_platform(argv[0], argv[1]).settings())

    def _change(self, argv):
        settings = self.get_collection(argv)
        handler = ChangeHandler(self._config)
        handler.change(settings)

    def _change_doc(self):
        return ActionDoc("change", self._list_params(), """
        Add, update or delete Settings.""")

    def _list_secret(self, argv):
        parameters = {}
        parameters["secret_only"] = True

        self._list(argv, parameters)

    def _list_non_secret(self, argv):
        parameters = {}
        parameters["no_secret"] = True
        
        self._list(argv, parameters)

    def _list_secret_doc(self):
        return ActionDoc("list_secret", "<org_name>", """
        List secret setting.""")
    
    def _list_non_secret_doc(self):
        return ActionDoc("list_non_secret", "<org_name>", """
        List non secret setting.""")


class OrganizationSettingsController(EntityController):

    _template = "setting.json"
    
    
    def __init__(self):
        super(OrganizationSettingsController, self).__init__()

        self._parameters = {}

        self._doc = "Settings handling."
        self._update_action_doc_params("list", "<org_name>")
        self._update_action_doc_params("add", "<org_name>")
        self._update_action_doc_params("delete", "<org_name> <setting_name>")
        self._update_action_doc_params("update", "<org_name> <setting_name>")
        self._update_action_doc_params("show", "<org_name> <setting_name>")

        self._register(["change"], self._change, self._print_list_completions)
        self._register_action_doc(self._change_doc())

        self._register(["impact"], self._impact, self._print_entity_completions)
        self._register_action_doc(self._impact_doc())

        self._register(["list-secret"], self._list_secret, self._print_list_completions)
        self._register_action_doc(self._list_secret_doc())

        self._register(["list-non-secret"], self._list_non_secret, self._print_list_completions)
        self._register_action_doc(self._list_non_secret_doc())


    def _get_name_argument(self, argv):
        if len(argv) < 2:
            raise ArgumentException("An organization and a setting name must be provided");

        return argv[1]

    def _get_value_argument(self, argv):
        if len(argv) < 3:
            return None

        return argv[2]

    def get_collection(self, argv):
        if len(argv) < 1:
            raise ArgumentException("An organization must be provided");

        return self._client.get_organization(argv[0]).settings()

    def _list_secret(self, argv):
        parameters = {}
        parameters["secret_only"] = True

        self._list(argv, parameters)

    def _list_non_secret(self, argv):
        parameters = {}
        parameters["no_secret"] = True

        self._list(argv, parameters)

    def _print_collection_completions(self, param_num, argv):
        if param_num == 0:
            completions.print_identifiers(self._client.organizations())

    def _print_entity_completions(self, param_num, argv):
        if param_num < 1:
            self._print_collection_completions(param_num, argv)
        elif len(argv) > 0 and param_num == 1:
            completions.print_identifiers(self._client.get_organization(argv[0]).settings())

    def _change(self, argv):
        settings = self.get_collection(argv)
        handler = ChangeHandler(self._config)
        handler.change(settings)

    def _change_doc(self):
        return ActionDoc("change", self._list_params(), """
        Add, update or delete Settings.""")


    def _impact(self, argv):
        res = self._client.get_organization(argv[0]).impact(argv[1])
        if self._config.options.raw:
            print(json.dumps(res.get_json(), indent=4))            
        else:
            res.show()        
    
    def _impact_doc(self):
        return ActionDoc("impact", "<org_name>", """
        Impact analysis if setting change.""")

    def _list_secret_doc(self):
        return ActionDoc("list_secret", "<org_name>", """
        List secret setting.""")
    
    def _list_non_secret_doc(self):
        return ActionDoc("list_non_secret", "<org_name>", """
        List non secret setting.""")

class ChangeHandler(object):

    def __init__(self, config):
        self._config = config

    def change(self, settings):
        settings_list = settings.list()
        updater = JsonUpdater(self._config.options)
        updated_list = updater.update(JsonWrapper([s.get_json() for s in settings_list]))

        updated_settings = [settings._new(data) for data in updated_list]
        actions = self._build_actions(settings_list, updated_settings)
        if len(actions) > 0:
            self._print_actions(actions)
            if self._config.options.force or (prompt.confirm(prompt = "Do you want to proceed?", resp = False)):
                settings.change(updated_settings, self._config.options.no_delete)
        else:
            print("No change detected, ignoring")

    def _build_actions(self, initial_list, updated_list):
        initial_dict = {}
        for s in initial_list:
            initial_dict[s.key] = s
        updated_dict = {}
        for s in updated_list:
            updated_dict[s.key] = s

        actions = []
        for key in updated_dict:
            if key not in initial_dict:
                actions.append("- Adding setting " + key)
            elif self._value_changed(initial_dict[key], updated_dict[key]):
                actions.append("- Updating setting " + key)

        if not self._config.options.no_delete:
            for key in initial_dict:
                if key not in updated_dict:
                    actions.append("- Deleting setting " + key)

        return actions

    def _value_changed(self, setting_before, setting_after):
        type_before = type(setting_before)
        type_after = type(setting_after)
        if type_before != type_after:
            return True

        if type_before == SimpleSetting:
            return setting_before.value != setting_after.value
        elif type_before == LinkSetting:
            return setting_before.link != setting_after.link
        elif type_before == PropertySetting:
            return setting_before.property_f != setting_after.property_f
        else:
            raise ControllerException("Unsupported setting type: " + str(type_before))

    def _print_actions(self, actions):
        print("The following actions will be taken:")
        for a in actions:
            print(a)
