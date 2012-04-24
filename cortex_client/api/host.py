# coding: utf-8
"""
Host module. Provides classes representing a host, host's properties and host's
settings.

@organization: Guardis
@copyright: 2011 Guardis SPRL, Liège, Belgium.
"""

from cortex_client.rest.exceptions import ApiException
from cortex_client.util.json_wrapper import JsonWrapper, StringFactory
from exceptions import PythonApiException
from cortex_client.api.settings import Configurable, SettingFactory
from cortex_client.api.contexts import ApplicationContextCollection, \
    PlatformContextCollection, DistributionContextCollection
from cortex_client.api.resource import Resource
from cortex_client.api.collection import Collection
from cortex_client.api.audit import AuditCollection

class Property(JsonWrapper):
    """
    A host property. A property is composed of a key and a value.
    """
    def __init__(self, json_data = None):
        super(Property, self).__init__(json_data)

    def get_key(self):
        """
        Provides property's key.
        @return: The key
        @rtype: String
        """
        return self._get_field("key")

    def set_key(self, key):
        """
        Sets property's key.
        @param key: The key
        @type key: String
        """
        return self._set_field("key", key)

    def get_value(self):
        """
        Provides property's key.
        @return: The key
        @rtype: String
        """
        return self._get_field("value")

    def set_value(self, value):
        """
        Sets property's value.
        @param value: The value
        @type value: String
        """
        return self._set_field("value", value)

    def show(self, indent = 0):
        """
        Prints this property's state to standard output in a user-friendly way.

        @param indent: The number of spaces to put in front of each displayed
        line.
        @type indent: Integer
        """
        print " "*indent, "Key:", self.get_key()
        print " "*indent, "Value:", self.get_value()

class PropertyFactory(object):
    """
    Host's property factory.

    @see: L{Property}
    @see: L{cortex_client.util.json_wrapper.JsonWrapper._get_list_field}
    """
    def new_object(self, json_data):
        """
        Instantiates a L{Property} object using given state.

        @param json_data: A quasi-JSON representation of a Property instance's state.
        @type json_data: String, dict or list

        @return: A property
        @rtype: L{Property}
        """
        return Property(json_data)

class Vnc(JsonWrapper):
    def get_hostname(self):
        return self._get_field("hostname")

    def get_port(self):
        return self._get_field("port")

    def show(self, indent = 0):
        print " "*indent, "hostname:", self.get_hostname()
        print " "*indent, "port:", self.get_port()


class InstanceCollection(Collection):
    def __init__(self, api, collection_path):
        super(InstanceCollection, self).__init__(collection_path, api)

    def _new_resource(self, json_data):
        return Instance(self, json_data)


class Instance(Resource):
    """
    Runtime host instance information.
    """

    def __init__(self, collection, json_data = None):
        super(Instance, self).__init__(collection, json_data)

    def _get_path(self):
        return self._collection.get_path()

    def rename(self, new_name):
        raise PythonApiException("Renaming is unsupported for instance")

    def commit(self, force = False):
        raise PythonApiException("Committing is unsupported for instance")

    def create(self):
        """
        Creates a new resource on the server using this object's state for
        initialization.

        @raise PythonApiException: If server access point is not set.
        """
        props = self.get_properties()
        if len(props) == 0:
            self._collection.add_resource(self)
        else:
            self.set_json(self._get_client().create(self._get_path() + "properties", props))

    def get_state(self):
        """
        Provides the state of the instance.
        @return: Instance's state
        @rtype: String
        """
        return self._get_field("state")

    def get_ip(self, interface):
        props = self.get_properties()
        for p in props:
            if p.get_key() == "ip." + interface:
                return p.get_value()
        return None

    def get_hostname(self):
        return self._get_field("hostname")

    def get_vnc(self):
        return Vnc(self._get_field("vncView"))

    def get_synapse_state(self):
        """
        Provides Synapse's state.
        @return: Synapse's state (possible values: Up, Down)
        @rtype: String
        """
        return self._get_field("synapseState")

    def get_properties(self):
        return self._get_list_field("properties", PropertyFactory())

    def add_property(self, prop):
        self._add_to_list_field("properties", prop)

    def start(self):
        """
        Starts host.
        @raise PythonApiException: If host could not be started.
        """
        try:
            result = self._get_client().update(self._get_path() + "_start", decode = False)
            if(result.getcode() != 202):
                raise PythonApiException("Call not accepted by server")
        except ApiException, e:
            raise PythonApiException("Unable to start host: " + e.message)

    def pause(self):
        """
        Pauses host.
        @raise PythonApiException: If host could not be paused.
        """
        result = self._get_client().update(self._get_path() + "_pause", decode = False)
        if(result.getcode() != 202):
            raise PythonApiException("Call not accepted by server")

    def resume(self):
        """
        Resumes host's execution (after pause).
        @raise PythonApiException: If host's execution could not be resumed.
        """
        result = self._get_client().update(self._get_path() + "_resume", decode = False)
        if(result.getcode() != 202):
            raise PythonApiException("Call not accepted by server")

    def shutdown(self):
        """
        Shutdowns host.
        @raise PythonApiException: If host could not be shutdown.
        """
        result = self._get_client().update(self._get_path() + "_stop", decode = False)
        if(result.getcode() != 202):
            raise PythonApiException("Call not accepted by server")

    def poweroff(self):
        """
        Power-off host.
        @raise PythonApiException: If host could not be powered-off.
        """
        try:
            result = self._get_client().update(self._get_path() + "_off", decode = False)
            if(result.getcode() != 202):
                raise PythonApiException("Call not accepted by server")
        except ApiException, e:
            raise PythonApiException("Unable to poweroff host: " + e.message)

    def _show(self, indent = 0):
        """
        Prints instance's information to standard output in a user-friendly way.

        @param indent: The number of spaces to put in front of each displayed
        line.
        @type indent: Integer
        """
        print " "*indent, "State:", self.get_state()
        print " "*indent, "Synapse state:", self.get_synapse_state()
        print " "*indent, "Hostname:", self.get_hostname()
        print " "*indent, "Vnc:"
        self.get_vnc().show(indent + 2)

    def show_properties(self, indent = 0):
        print " "*indent, "Properties:"
        props = self.get_properties()
        for p in props:
            print " "*(indent + 2), p.get_key(), ":", p.get_value()


class Task(JsonWrapper):
    def __init__(self, json_data = None):
        super(Task, self).__init__(json_data)

    def get_order_num(self):
        return int(self._get_field("orderNum"))

    def get_description(self):
        return self._get_field("description")

    def get_status(self):
        return self._get_field("status")

    def show(self, indent = 0):
        print " "*indent, "Number:", self.get_order_num()
        print " "*indent, "Description:", self.get_description()
        print " "*indent, "Status:", self.get_status()

class TaskFactory(object):
    def new_object(self, json_data):
        return Task(json_data)


class Change(JsonWrapper):
    def __init__(self, json_data = None):
        super(Change, self).__init__(json_data)

    def get_order_num(self):
        return int(self._get_field("orderNum"))

    def get_description(self):
        return self._get_field("description")

    def get_tasks(self):
        return self._get_list_field("tasks", TaskFactory())

    def show(self, indent = 0):
        print " "*indent, "Number:", self.get_order_num()
        print " "*indent, "Description:", self.get_description()
        print " "*indent, "Tasks:"
        tasks = self.get_tasks()
        for t in tasks:
            t.show(indent + 2)


class Host(Configurable):
    """
    A host. A host is part of an environment and has settings and properties
    associated to it. It features a list of installed applications, is associated
    to a platform and a distribution. It may be started, paused, resumed, shutdown
    and provisioned.
    """
    def __init__(self, collection, json_data = None):
        """
        @param api: An access point.
        @type api: L{CortexApi}
        @param json_data: A quasi-JSON representation of application's state.
        @type json_data: dict, list or String
        """
        super(Host, self).__init__(collection, json_data)

    def get_organization(self):
        """
        Provides the organization this host is part of. It is this host's
        environment's organization.
        @return: Organization's UUID
        @rtype: String
        """
        return self._get_field("organization")

    def set_organization(self, name):
        return self._set_field("organization", name)

    def get_environment(self):
        """
        Provides the environment this host is part of.
        @return: Environment's UUID
        @rtype: String
        """
        return self._get_field("environment")

    def set_environment(self, name):
        return self._set_field("environment", name)

    def get_platform(self):
        """
        Provides the environment this host is part of.
        @return: Environment's UUID
        @rtype: String
        """
        return self._get_field("platform")

    def set_platform(self, platform):
        """
        Sets host's platform.
        @param platform: Platform's UUID
        @type platform: String
        """
        self._set_field("platform", platform)

    def set_platform_context(self, context):
        try:
            self._get_client().create(self._get_path() + "platform/", context)
        except ApiException, e:
            raise PythonApiException("Could not set distribution context: " + e.message)

    def get_distribution(self):
        """
        Provides the environment this host is part of.
        @return: Environment's UUID
        @rtype: String
        """
        return self._get_field("distribution")

    def set_distribution(self, distribution):
        """
        Sets host's distribution.
        @param distribution: Distribution's UUID
        @type distribution: String
        """
        self._set_field("distribution", distribution)

    def set_distribution_context(self, context):
        try:
            self._get_client().create(self._get_path() + "distribution/", context)
        except ApiException, e:
            raise PythonApiException("Could not set distribution context: " + e.message)

    def get_settings(self):
        """
        Provides host's settings.
        @return: Host's settings.
        @rtype: list of L{Setting}
        """
        return self._get_list_field("settings", SettingFactory(None))

    def add_setting(self, setting):
        """
        Adds a setting to host. Note that, for a provisioned host, settings must
        be added, removed and/or updated using change requests.
        @param setting: A setting.
        @type setting: {Setting}
        """
        self._add_to_list_field("settings", setting)

    def get_applications(self):
        """
        Provides host's applications.
        @return: Application names
        @rtype: list of L{String}
        """
        return self._get_list_field("applications", StringFactory())

    def set_applications(self, applications):
        """
        Sets host's applications. Note that, for a provisioned host, applications
        must be added or removed using change requests.
        @param applications: Host's applications.
        @type applications: list of L{String}
        """
        self._set_list_field("applications", applications)

    def add_application(self, app_name):
        """
        Adds an application to this host. Note that, for a provisioned host,
        applications must be added or removed using change requests.
        @param application: An application's name
        @type application: L{String}
        """
        self._add_to_list_field("applications", app_name)

    def get_version(self):
        """
        Provides the version number of this host.
        @return: Host's version number
        @rtype: Integer
        """
        return int(self._get_field("version"))

    def delete(self):
        """
        Deletes this host.
        """
        try:
            self._get_client().delete(self._get_path())
        except ApiException, e:
            raise PythonApiException("Unable to delete host: " + e.message)

    def get_state(self):
        """
        Provides host's state.
        @return: Host's state
        @rtype: String
        """
        return self._get_field("state")

    def clear_state(self):
        self._del_field("state")

    def instance(self):
        """
        Provides host's instance information.
        @return: Host's instance information.
        @rtype: L{InstanceInfo}
        @raise PythonApiException: If host was not yet provisioned
        """
        return InstanceCollection(self._get_api(), self._get_path() + "instance/")

    def _show(self, indent = 0):
        print " "*indent, "Name:", self.get_name()
        print " "*indent, "Description:", self.get_description()
        print " "*indent, "Organization:", self.get_organization()
        print " "*indent, "Environment:", self.get_environment()
        print " "*indent, "Platform:", self.get_platform()
        print " "*indent, "Distribution:", self.get_distribution()
        print " "*indent, "State:", self.get_state()

    def show_settings(self, indent = 0):
        """
        Prints Host's settings to standard output in a user-friendly way.

        @param indent: The number of spaces to put in front of each displayed
        line.
        @type indent: Integer
        """
        print " "*indent, "Settings:"
        settings = self.get_settings()
        for s in settings:
            s.show(indent = (indent + 2))
            print

    def show_applications(self, indent = 0):
        print " "*indent, "Applications:"
        apps = self.get_applications()
        for app in apps:
            print " "*(indent + 2), app

    def set_instance_properties(self, props):
        client = self._get_client()
        try:
            client.create(self._get_path() + "instance/properties", props, decode = False)
        except ApiException, e:
            raise PythonApiException("Unable to set instance properties: " + e.message)

    def provision(self):
        """
        Provisions host.
        @raise PythonApiException: If host could not be provisioned.
        """
        instance = self.instance()._new_resource({})
        instance.create()

    def __render_file(self, collection, file_name):
        try:
            result = self._get_client().read(collection + "/files/" + file_name, decode = False)
            return result
        except ApiException, e:
            raise PythonApiException("Unable to render file: " + e.message)

    def render_app_file(self, app_name, file_name):
        return self.__render_file(self._get_path() + "applications/" + app_name, file_name)

    def render_dist_file(self, file_name):
        return self.__render_file(self._get_path() + "distribution", file_name)

    def render_plat_file(self, file_name):
        return self.__render_file(self._get_path() + "platform", file_name)

    def render_kickstart(self):
        try:
            result = self._get_client().read(self._get_path() + "kickstart", decode = False)
            return result
        except ApiException, e:
            raise PythonApiException("Unable to render kickstart: " + e.message)

    def clone(self):
        try:
            result = self._get_client().update(self._get_path() + "_clone")
            return Host(self._collection, result)
        except ApiException, e:
            raise PythonApiException("Unable to clone host: " + e.message)

    def applications(self):
        return ApplicationContextCollection(self._get_api(), self._get_path() + "applications/")

    def platform(self):
        return PlatformContextCollection(self._get_api(), self._get_path() + "platform/")

    def distribution(self):
        return DistributionContextCollection(self._get_api(), self._get_path() + "distribution/")

    def get_changes(self, show_processed = False):
        if self.get_state() != "PROVISIONED":
            raise PythonApiException("Host must be provisioned")

        try:
            json_changes = self._get_client().read(self._get_path() + "changes/",
                                                   {"show_processed" : "true" if show_processed else "false"})
            changes = []
            if json_changes["count"] == "0":
                return changes

            for json_change in json_changes["items"]:
                changes.append(Change(json_change))
            return changes
        except ApiException, e:
            raise PythonApiException("Unable to get changes: " + e.message)

    def clear_changes(self):
        if self.get_state() != "PROVISIONED":
            raise PythonApiException("Host must be provisioned")
        self._get_client().delete(self._get_path() + "changes/")

    def clear_change(self, order_num):
        if self.get_state() != "PROVISIONED":
            raise PythonApiException("Host must be provisioned")
        self._get_client().delete(self._get_path() + "changes/" + str(order_num))

    def audit_logs(self):
        return AuditCollection(self._get_path() + "audit/", self._get_api())

