# coding: utf-8

from __future__ import print_function
from __future__ import absolute_import
from builtins import str
from builtins import object
from . import completions
import re
from collections import OrderedDict
import json, os
import sys
from comodit_client.util.editor import edit_text
from comodit_client.config import Config
from comodit_client.control.entity import EntityController
from comodit_client.control.exceptions import ArgumentException, ControllerException
from comodit_client.control.doc import ActionDoc
from comodit_client.control.json_update import JsonUpdater
from comodit_client.util.json_wrapper import JsonWrapper
from comodit_client.util import prompt
from comodit_client.api.settings import SimpleSetting, LinkSetting, PropertySetting


class SettingController(EntityController):

    _template = "setting.json"

    def __init__(self):
        super(SettingController, self).__init__()

        self._doc = "Settings handling."
        self._update_action_doc_params("add", self._print_list_doc())
        self._update_action_doc_params("delete", self._print_entity_doc())
        self._update_action_doc_params("update", self._print_entity_doc())
        self._update_action_doc_params("show", self._print_entity_doc())

        self._register(["change"], self._change, self._print_entity_doc)
        self._register_action_doc(self._change_doc())

        self._register(["impact"], self._impact, self._print_entity_completions)
        self._register_action_doc(self._impact_doc())
        self._register_action_doc(self._list_setting_doc())

    def _list(self, argv, parameters=None):
        if parameters is None:
            parameters = self._get_list_parameters(argv)

        options = self._config.options
        parameters["secret_only"] = options.secret
        parameters["no_secret"] = options.non_secret
        parameters["obfuscate"] = options.obfuscate
        if options.key is not None:
            parameters["key"] = options.key

        entities_list = self._list_entities(argv, parameters=parameters)
        if entities_list:
            self._print_entities(entities_list)

        res = self.get_application_property_collection(argv).list(parameters=parameters)
        if res:
            self._print_entities(res)

    def _print_entities(self, entities_list):
        if self._config.options.raw:
            print(json.dumps([entity.get_json() for entity in entities_list], indent=4))
        else:
            if len(entities_list) == 0:
                print(self._str_empty)
            else:
                for e in sorted(entities_list, key=self._sort_key()):
                    print(self._label(e))

    def _get_entity(self, argv, parameters={}):
        parameters = self._get_show_parameters(argv)

        options = self._config.options
        parameters["secret_only"] = options.secret
        parameters["no_secret"] = options.non_secret
        parameters["obfuscate"] = options.obfuscate

        key = self._get_name_argument(argv)
        if key.startswith("_application[") and '.package[' in key:
            return self.get_package_property(argv, key, parameters)
        elif key.startswith("_application[") and '.rpmModule[' in key:
            return self.get_rpm_property(argv, key, parameters)
        else:
            return self.get_collection(argv).get(self._get_name_argument(argv), parameters=parameters)

    def _add(self, argv):
        options = self._config.options

        if options.filename:
            with open(options.filename, 'r') as f:
                item = json.load(f, object_pairs_hook=OrderedDict)
        elif options.json:
            item = json.loads(options.json, object_pairs_hook=OrderedDict)
        elif options.stdin:
            item = json.load(sys.stdin, object_pairs_hook=OrderedDict)
        else:
            template_json = json.load(open(os.path.join(Config()._get_templates_path(), self._template)))
            self._complete_template(argv, template_json)
            updated = edit_text(json.dumps(template_json, indent=4))
            item = json.loads(updated, object_pairs_hook=OrderedDict)
        key = item["key"]
        if key.startswith("_application["):
            res = self.get_application_resource_property_collection(argv)._new(item)
            x = re.split("].", key)
            application = self._get_value_of_key(x[0])
            res.application = application
            res.key = x[2]
            resource = self._get_value_of_key(x[1])
            if ".package[" in key:
                res.package_name = resource
            elif ".rpmModule[" in key:
                res.rpm_module = resource
        else:
            res = self.get_collection(argv)._new(item)

        parameters = {}
        if options.populate:
            parameters["populate"] = "true"
        if options.default:
            parameters["default"] = "true"
        if options.test:
            parameters["test"] = "true"
        if options.orchestration_handler:
            parameters["trigger_orchestration_handler"] = "true"
            parameters["trigger_application_handler"] = "false"
        if options.non_handler:
            parameters["trigger_orchestration_handler"] = "false"
            parameters["trigger_application_handler"] = "false"
        if options.flavor != None:
            parameters["flavor"] = options.flavor

        res.create(parameters=parameters)
        res.show(as_json=options.raw)

    def get_package_property(self, argv, key, parameters):
        raise NotImplementedError

    def get_rpm_property(self, argv, key, parameters):
        raise NotImplementedError

    def _get_value_of_key(self, txt):
        start = txt.find('[') + 1
        return txt[start:len(txt)]

    def _impact(self, argv):
        key = self._get_name_argument(argv)
        if key.startswith("_application["):
            x = re.split("].", key)
            application = self._get_value_of_key(x[0])
            resource = self._get_value_of_key(x[1])
            if '.package[' in key:
                path = "applications/" + application + "/packages/" + resource + "/properties/" + x[2]
            elif '.rpmModule[' in key:
                path = "applications/" + application + "/rpmmodules/" + resource + "/properties/" + x[2]

            res = self._get_application_resource_impact(argv, path)
        else:
            res = self._get_setting_impact(argv)

        if self._config.options.raw:
            print(json.dumps(res.get_json(), indent=4))
        else:
            res.show()

    def _get_application_resource_impact(self, argv, path):
        raise NotImplementedError

    def _get_setting_impact(self, argv):
        raise NotImplementedError

    def get_application_property_collection(self, argv):
        raise NotImplementedError

    def get_application_resource_property_collection(self, argv):
        raise NotImplementedError

    def _print_list_doc(self):
        raise NotImplementedError

    def _print_entity_doc(self):
        raise NotImplementedError


class HostAbstractSettingsController(EntityController):
    _template = "setting.json"

    def __init__(self):
        super(HostAbstractSettingsController, self).__init__()

        self._doc = "Settings handling."
        self._update_action_doc_params("add", "<org_name> <env_name> <host_name>")
        self._update_action_doc_params("delete", "<org_name> <env_name> <host_name> <setting_name>")
        self._update_action_doc_params("update", "<org_name> <env_name> <host_name> <setting_name>")
        self._update_action_doc_params("show", "<org_name> <env_name> <host_name> <setting_name>")

        self._register(["change"], self._change, self._print_list_completions)
        self._register_action_doc(self._change_doc())
        self._register_action_doc(self._list_setting_doc())

    def _get_name_argument(self, argv):
        if len(argv) < 4:
            raise ArgumentException("An organization, an environment, a host and a setting name must be provided")
        return argv[3]

    def _get_value_argument(self, argv):
        if len(argv) < 5:
            return None

        return argv[4]

    def get_collection(self, argv):
        if len(argv) < 3:
            raise ArgumentException("An organization, an environment and a host must be provided")

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

    def _list_setting_doc(self):
        return ActionDoc("list", "<org_name> <env_name> <host_name> [--secret] [--non-secret] [--key]", """
        List available settings. 
        --secret return only secret settings
        --non-secret return only non secret setting
        --obfuscate obfuscate value for secret setting
        --key option add filter on setting key""")


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

        self._update_action_doc_params("add", "<org_name> <env_name> <host_name> <app_name>")
        self._update_action_doc_params("delete", "<org_name> <env_name> <host_name> <app_name> <setting_name>")
        self._update_action_doc_params("update", "<org_name> <env_name> <host_name> <app_name> <setting_name>")
        self._update_action_doc_params("show", "<org_name> <env_name> <host_name> <app_name> <setting_name>")

        self._register(["change"], self._change, self._print_list_completions)
        self._register(["show-origin"], self._show_origin, self._print_entity_completions)
        self._register_action_doc(self._change_doc())
        self._register_action_doc(self._show_origin_doc())
        self._register_action_doc(self._list_setting_doc())

    def _list_setting_doc(self):
        return ActionDoc("list", "<org_name> <env_name> <host_name> <app_name> [--secret] [--non-secret] [--key]", """
        List available settings. 
        --secret return only secret settings
        --non-secret return only non secret setting
        --obfuscate obfuscate value for secret setting
        --key option add filter on setting key""")

    def _get_name_argument(self, argv):
        if len(argv) < 5:
            raise ArgumentException(
                "An organization, an environment, a host, an application and a setting name must be provided");

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

    def _show_origin_doc(self):
        return ActionDoc("show-origin", self._list_params(), """
        Show origin and value for Settings.""")

    def _show_origin(self, argv):
        parameters = self._get_show_parameters(argv)
        res = self._client.get_host(argv[0], argv[1], argv[2]) \
            .get_application(argv[3]).setting_origin(argv[4], parameters)

        if self._config.options.raw:
            print(json.dumps(res.get_json(), indent=4))
        else:
            res.show()


class HostSettingsController(SettingController):

    def _print_list_doc(self):
        return "<org_name> <env_name> <host_name> <setting_name>"

    def _print_entity_doc(self):
        return "<org_name> <env_name> <host_name>"

    def _list_setting_doc(self):
        return ActionDoc("list", "<org_name>  <env_name> <host_name> [--secret] [--non-secret] [--key]", """
        List available settings. 
        --secret return only secret settings
        --non-secret return only non secret setting
        --obfuscate obfuscate value for secret setting
        --key option add filter on setting key""")

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
            completions.print_identifiers(self._client.get_host(argv[0], argv[1], argv[2]).application_properties)

    def _change(self, argv):
        settings = self.get_collection(argv)
        handler = ChangeHandler(self._config)
        handler.change(settings)

    def _change_doc(self):
        return ActionDoc("change", self._list_params(), """
        Add, update or delete Settings.""")

    def _impact_doc(self):
        return ActionDoc("impact", "<org_name> <env_name> <host_name> <setting_name>", """
        Impact analysis if setting change.""")

    def _get_application_resource_impact(self, argv, path):
        return self._client.get_host(argv[0], argv[1], argv[2]).resource_impact(path)

    def get_rpm_property(self, argv, key, parameters):
        x = re.split("].", key)
        application = self._get_value_of_key(x[0])
        resource = self._get_value_of_key(x[1])
        return self._client.get_host(argv[0], argv[1], argv[2]).rpm_module(application, resource, x[2])

    def get_package_property(self, argv, key, parameters):
        x = re.split("].", key)
        application = self._get_value_of_key(x[0])
        resource = self._get_value_of_key(x[1])
        return self._client.get_host(argv[0], argv[1], argv[2]).package(application, resource, x[2])

    def _get_setting_impact(self, argv):
        return self._client.get_host(argv[0], argv[1], argv[2]).impact()

    def get_application_property_collection(self, argv):
        if len(argv) < 3:
            raise ArgumentException("An organization and an environment must be provided")

        return self._client.get_host(argv[0], argv[1], argv[2]).application_properties

    def get_application_resource_property_collection(self, argv):
        if len(argv) < 3:
            raise ArgumentException("An organization and an environment must be provided")

        return self._client.get_host(argv[0], argv[1], argv[2]).resource_properties


class EnvironmentSettingsController(SettingController):


    def _get_application_resource_impact(self, argv, path):
        return self._client.get_environment(argv[0], argv[1]).resource_impact(path)

    def _get_setting_impact(self, argv):
        return self._client.get_environment(argv[0], argv[1]).impact(argv[2])

    def _print_list_doc(self):
        return "<org_name> <env_name>"

    def _print_entity_doc(self):
        return "<org_name> <env_name> <setting_name>"

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
            raise ArgumentException("An organization and an environment must be provided")

        return self._client.get_environment(argv[0], argv[1]).settings()

    def get_application_property_collection(self, argv):
        if len(argv) < 2:
            raise ArgumentException("An organization and an environment must be provided")

        return self._client.get_environment(argv[0], argv[1]).application_properties

    def get_application_resource_property_collection(self, argv):
        if len(argv) < 2:
            raise ArgumentException("An organization and an environment must be provided")

        return self._client.get_environment(argv[0], argv[1]).resource_properties

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
            completions.print_identifiers(self._client.get_environment(argv[0], argv[1]).application_properties)

    def _change(self, argv):
        settings = self.get_collection(argv)
        handler = ChangeHandler(self._config)
        handler.change(settings)

    def _change_doc(self):
        return ActionDoc("change", self._list_params(), """
        Add, update or delete Settings.""")

    def _impact_doc(self):
        return ActionDoc("impact", "<org_name> <env_name> <setting_name>", """
        Impact analysis if setting change.""")

    def _list_setting_doc(self):
        return ActionDoc("list", "<org_name> <env_name> [--secret] [--non-secret] [--key]", """
        List available settings. 
        --secret return only secret settings
        --non-secret return only non secret setting
        --obfuscate obfuscate value for secret setting
        --key option add filter on setting key""")

    def get_rpm_property(self, argv, key, parameters):
        x = re.split("].", key)
        application = self._get_value_of_key(x[0])
        resource = self._get_value_of_key(x[1])
        return self._client.get_environment(argv[0], argv[1]).rpm_module(application, resource, x[2])

    def get_package_property(self, argv, key, parameters):
        x = re.split("].", key)
        application = self._get_value_of_key(x[0])
        package = self._get_value_of_key(x[1])
        return self._client.get_environment(argv[0], argv[1]).package(application, package, x[2])


class HostGroupSettingsController(SettingController):

    def _get_name_argument(self, argv):
        if len(argv) < 3:
            raise ArgumentException("An organization, a hostgroup and a setting name must be provided");

        return argv[2]

    def _get_value_argument(self, argv):
        if len(argv) < 4:
            return None

        return argv[3]

    def get_collection(self, argv):
        if len(argv) < 2:
            raise ArgumentException("An organization and an hostgroup must be provided");

        return self._client.get_host_group(argv[0], argv[1]).settings()

    def _print_collection_completions(self, param_num, argv):
        if param_num == 0:
            completions.print_identifiers(self._client.organizations())
        elif len(argv) > 0 and param_num == 1:
            completions.print_identifiers(self._client.host_groups(argv[0]))

    def _print_entity_completions(self, param_num, argv):
        if param_num < 2:
            self._print_collection_completions(param_num, argv)
        elif len(argv) > 1 and param_num == 2:
            completions.print_identifiers(self._client.get_host_group(argv[0], argv[1]).settings())
            completions.print_identifiers(self._client.get_host_group(argv[0], argv[1]).application_properties)

    def _change(self, argv):
        settings = self.get_collection(argv)
        handler = ChangeHandler(self._config)
        handler.change(settings)

    def _change_doc(self):
        return ActionDoc("change", self._list_params(), """
        Add, update or delete Settings.""")

    def _impact_doc(self):
        return ActionDoc("impact", "<org_name> <hostgroup_name> <setting_name>", """
        Impact analysis if setting change.""")

    def _list_setting_doc(self):
        return ActionDoc("list", "<org_name> <hostgroup_name> [--secret] [--non-secret] [--key]", """
        List available settings. 
        --secret return only secret settings
        --non-secret return only non secret setting
        --obfuscate obfuscate value for secret setting
        --key option add filter on setting key""")

    def get_package_property(self, argv, key, parameters):
        x = re.split("].", key)
        application = self._get_value_of_key(x[0])
        resource = self._get_value_of_key(x[1])
        return self._client.get_host_group(argv[0], argv[1]).package(application, resource, x[2])

    def get_rpm_property(self, argv, key, parameters):
        x = re.split("].", key)
        application = self._get_value_of_key(x[0])
        resource = self._get_value_of_key(x[1])
        return self._client.get_host_group(argv[0], argv[1]).rpm_module(application, resource, x[2])

    def _get_setting_impact(self, argv):
        return self._client.get_host_group(argv[0], argv[1]).impact()

    def get_application_property_collection(self, argv):
        if len(argv) < 2:
            raise ArgumentException("An organization and an hostgroup must be provided")

        return self._client.get_host_group(argv[0], argv[1]).application_properties

    def get_application_resource_property_collection(self, argv):
        if len(argv) < 2:
            raise ArgumentException("An organization and an hostgroup must be provided")

        return self._client.get_host_group(argv[0], argv[1]).resource_properties

    def _get_application_resource_impact(self, argv, path):
        return self._client.get_host_group(argv[0], argv[1]).resource_impact(path)

    def _print_list_doc(self):
        return "<org_name> <hostgroup_name> <setting_name>"

    def _print_entity_doc(self):
        return "<org_name> <hostgroup_name>"


class DistributionSettingsController(EntityController):
    _template = "setting.json"

    def __init__(self):
        super(DistributionSettingsController, self).__init__()

        self._doc = "Settings handling."
        self._update_action_doc_params("add", "<org_name> <dist_name>")
        self._update_action_doc_params("delete", "<org_name> <dist_name> <setting_name>")
        self._update_action_doc_params("update", "<org_name> <dist_name> <setting_name>")
        self._update_action_doc_params("show", "<org_name> <dist_name> <setting_name>")

        self._register(["change"], self._change, self._print_list_completions)
        self._register_action_doc(self._change_doc())
        self._register_action_doc(self._list_setting_doc())

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

    def _list_setting_doc(self):
        return ActionDoc("list", "<org_name> <dist_name> [--secret] [--non-secret] [--key]", """
        List available settings. 
        --secret return only secret settings
        --non-secret return only non secret setting
        --obfuscate obfuscate value for secret setting
        --key option add filter on setting key""")


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
        self._register_action_doc(self._list_setting_doc())

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

    def _list_setting_doc(self):
        return ActionDoc("list", "<org_name> <plat_name> [--secret] [--non-secret] [--key]", """
        List available settings. 
        --secret return only secret settings
        --non-secret return only non secret setting
        --obfuscate obfuscate value for secret setting
        --key option add filter on setting key""")


class OrganizationSettingsController(SettingController):

    def __init__(self):
        super(OrganizationSettingsController, self).__init__()

        self._parameters = {}

        self._doc = "Settings handling."
        self._update_action_doc_params("add", "<org_name>")
        self._update_action_doc_params("delete", "<org_name> <setting_name>")
        self._update_action_doc_params("update", "<org_name> <setting_name>")
        self._update_action_doc_params("show", "<org_name> <setting_name>")

        self._register(["change"], self._change, self._print_list_completions)
        self._register_action_doc(self._change_doc())

        self._register(["impact"], self._impact, self._print_entity_completions)
        self._register_action_doc(self._impact_doc())

        self._register(["tree"], self._tree, self._print_list_completions)
        self._register_action_doc(self._tree_doc())

        self._register_action_doc(self._list_setting_doc())

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

    def _print_collection_completions(self, param_num, argv):
        if param_num == 0:
            completions.print_identifiers(self._client.organizations())

    def _print_entity_completions(self, param_num, argv):
        if param_num < 1:
            self._print_collection_completions(param_num, argv)
        elif len(argv) > 0 and param_num == 1:
            completions.print_identifiers(self._client.get_organization(argv[0]).settings())
            completions.print_identifiers(self._client.get_organization(argv[0]).application_properties)

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

    def _list_setting_doc(self):
        return ActionDoc("list", "<org_name> [--secret] [--non-secret] [--key]", """
        List available settings. 
        --secret return only secret settings
        --non-secret return only non secret setting
        --obfuscate obfuscate value for secret setting
        --key option add filter on setting key""")

    def _tree(self, argv):
        paramters = self._get_list_parameters(argv)

        if len(argv) < 1:
            raise ArgumentException("An organization must be provided");

        entity = self._client.get_organization(argv[0]).tree(self._config.options.secret,
                                                             self._config.options.non_secret, self._config.options.key)

        if self._config.options.raw:
            print(json.dumps(entity.get_json(), indent=4))
        else:
            entity.show()

    def _tree_doc(self):
        return ActionDoc("tree", "<org_name>  [--secret] [--non-secret] [--key]", """
        Get a tree of each setting in organization.
        --secret return only secret setting
        --non-secret return only non secret setting
        --key option add filter on setting key""")

    def get_package_property(self, argv, key, parameters):
        x = re.split("].", key)
        application = self._get_value_of_key(x[0])
        resource = self._get_value_of_key(x[1])
        return self._client.get_organization(argv[0]).package(application, resource, x[2])

    def get_rpm_property(self, argv, key, parameters):
        x = re.split("].", key)
        application = self._get_value_of_key(x[0])
        resource = self._get_value_of_key(x[1])
        return self._client.get_organization(argv[0]).rpm_module(application, resource, x[2])

    def _get_setting_impact(self, argv):
        return self._client.get_organization(argv[0]).impact()

    def get_application_property_collection(self, argv):
        if len(argv) < 1:
            raise ArgumentException("An organization must be provided")

        return self._client.get_organization(argv[0]).application_properties

    def get_application_resource_property_collection(self, argv):
        if len(argv) < 1:
            raise ArgumentException("An organization must be provided")

        return self._client.get_organization(argv[0]).resource_properties

    def _get_application_resource_impact(self, argv, path):
        return self._client.get_organization(argv[0]).resource_impact(path)

    def _print_list_doc(self):
        return "<org_name> "

    def _print_entity_doc(self):
        return "<org_name> <setting_name>"

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
            if self._config.options.force or (prompt.confirm(prompt="Do you want to proceed?", resp=False)):
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
