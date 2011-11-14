# coding: utf-8
"""
Host module. Provides classes representing a host, host's properties and host's
settings.

@organization: Guardis
@copyright: 2011 Guardis SPRL, Liège, Belgium.
"""

from cortex_client.api.resource import Resource
from cortex_client.rest.exceptions import ApiException
from cortex_client.util.json_wrapper import JsonWrapper, StringFactory
from exceptions import PythonApiException

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

class Setting(JsonWrapper):
    """
    A host's setting. A setting has a key, a value and a version number. Note
    that in order to add a setting to a host, a change request must be used. Same
    applies to setting's deletion and update. Therefore, a setting does not
    feature setters.
    """
    def __init__(self, json_data = None):
        super(Setting, self).__init__(json_data)

    def get_value(self):
        """
        Provides setting's value.
        @return: The value
        @rtype: String
        """
        return self._get_field("value")

    def get_key(self):
        """
        Provides setting's key.
        @return: The key
        @rtype: String
        """
        return self._get_field("key")

    def get_version(self):
        """
        Provides setting's version number.
        @return: The version number
        @rtype: Integer
        """
        return int(self._get_field("version"))

    def show(self, indent = 0):
        """
        Prints this property's state to standard output in a user-friendly way.
        
        @param indent: The number of spaces to put in front of each displayed
        line.
        @type indent: Integer
        """
        print " "*indent, "Key:", self.get_key()
        print " "*indent, "Value:", self.get_value()
        print " "*indent, "Version:", self.get_version()


class SettingFactory(object):
    """
    Host's setting factory.
    
    @see: L{Setting}
    @see: L{cortex_client.util.json_wrapper.JsonWrapper._get_list_field}
    """
    def new_object(self, json_data):
        """
        Instantiates a L{Setting} object using given state.
        
        @param json_data: A quasi-JSON representation of a Property instance's state.
        @type json_data: String, dict or list
        
        @return: A setting
        @rtype: L{Setting}
        """
        return Setting(json_data)


class InstanceInfo(JsonWrapper):
    """
    Runtime host instance information.
    """

    def get_state(self):
        """
        Provides the state of the instance.
        @return: Instance's state
        @rtype: String
        """
        return self._get_field("state")

    def get_platform_hostname(self):
        """
        Provides instance's platform host name.
        @return: A platform state
        @rtype: String
        """
        return self._get_field("platformHostName")

    def get_vnc_port(self):
        """
        Provides VNC port of the instance
        @return: A port
        @rtype: Integer
        """
        return int(self._get_field("vncPort"))

    def get_synapse_state(self):
        """
        Provides Synapse's state.
        @return: Synapse's state (possible values: Up, Down)
        @rtype: String
        """
        return self._get_field("synapseState")

    def show(self, indent = 0):
        """
        Prints instance's information to standard output in a user-friendly way.
        
        @param indent: The number of spaces to put in front of each displayed
        line.
        @type indent: Integer
        """
        print " "*indent, "State:", self.get_state()
        print " "*indent, "Platform host name:", self.get_platform_hostname()
        print " "*indent, "VNC port:", self.get_vnc_port()
        print " "*indent, "Synapse state:", self.get_synapse_state()

class Host(Resource):
    """
    A host. A host is part of an environment and has settings and properties
    associated to it. It features a list of installed applications, is associated
    to a platform and a distribution. It may be started, paused, resumed, shutdown
    and provisioned.
    """
    def __init__(self, api = None, json_data = None):
        """
        @param api: An access point.
        @type api: L{CortexApi}
        @param json_data: A quasi-JSON representation of application's state.
        @type json_data: dict, list or String
        """
        super(Host, self).__init__(json_data)
        if(api):
            self.set_api(api)

    def set_api(self, api):
        super(Host, self).set_api(api)
        self._set_collection(api.get_host_collection())

    def get_organization(self):
        """
        Provides the organization this host is part of. It is this host's
        environment's organization.
        @return: Organization's UUID
        @rtype: String
        """
        return self._get_field("organization")

    def set_organization(self, organization):
        """
        Sets the organization this host is part of. It must be host's
        environment's organization.
        @param organization: Organization's UUID
        @type organization: String
        """
        self._set_field("organization", organization)

    def get_environment(self):
        """
        Provides the environment this host is part of.
        @return: Environment's UUID
        @rtype: String
        """
        return self._get_field("environment")

    def set_environment(self, environment):
        """
        Sets the environment this host is part of.
        @param environment: Environment's UUID
        @type environment: String
        """
        self._set_field("environment", environment)

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

    def get_settings(self):
        """
        Provides host's settings.
        @return: Host's settings.
        @rtype: list of L{Setting}
        """
        return self._get_list_field("settings", SettingFactory())

    def set_settings(self, settings):
        """
        Sets host's settings. Note that, for a provisioned host, settings must
        be added, removed and/or updated using change requests.
        @return: Host's settings.
        @rtype: list of L{Setting}
        """
        self._set_list_field("settings", settings)

    def add_setting(self, setting):
        """
        Adds a setting to host. Note that, for a provisioned host, settings must
        be added, removed and/or updated using change requests.
        @param setting: A setting.
        @type setting: {Setting}
        """
        self._add_to_list_field("settings", setting)

    def get_properties(self):
        """
        Provides host's properties.
        @return: Host's properties.
        @rtype: list of L{Property}
        """
        return self._get_list_field("properties", PropertyFactory())

    def set_properties(self, properties):
        """
        Sets host's properties. Properties are generally set and handled
        by cortex server.
        Modifying this values is therefore potentially dangerous.
        @param properties: Host's new properties.
        @type properties: list of L{Property}
        """
        self._set_list_field("properties", properties)

    def add_property(self, prop):
        """
        Adds a property to this host. Properties are generally set  and handled
        by cortex server. Modifying this values is therefore potentially dangerous.
        @param prop: A property.
        @type prop: L{Property}
        """
        self._add_to_list_field("properties", prop)

    def get_applications(self):
        """
        Provides host's applications.
        @return: Host's applications.
        @rtype: list of L{Application}
        """
        return self._get_list_field("applications", StringFactory())

    def set_applications(self, applications):
        """
        Sets host's applications. Note that, for a provisioned host, applications
        must be added or removed using change requests.
        @param applications: Host's applications.
        @type applications: list of L{Application}
        """
        self._set_list_field("applications", applications)

    def add_application(self, application):
        """
        Adds an application to this host. Note that, for a provisioned host,
        applications must be added or removed using change requests.
        @param application: An application
        @type application: L{Application}
        """
        self._add_to_list_field("applications", application)

    def get_version(self):
        """
        Provides the version number of this host.
        @return: Host's version number
        @rtype: Integer
        """
        return int(self._get_field("version"))

    def delete(self, delete_vm = False):
        """
        Deletes this host. Associated VM may also be destroyed.
        @param delete_vm: If True, VM associated to this host is destroyed.
        """
        if(delete_vm):
            try:
                self._api.get_client().update("hosts/" + self.get_uuid() + "/VM/_delete",
                                              decode = False)
            except ApiException, e:
                if(e.code == 400):
                    print "Could not delete VM:", e.message
                else:
                    raise e
        self._api.get_client().delete("hosts/" + self.get_uuid())

    def get_state(self):
        """
        Provides host's state.
        @return: Host's state
        @rtype: String
        """
        return self._get_field("state")

    def get_instance_info(self):
        """
        Provides host's instance information.
        @return: Host's instance information.
        @rtype: L{InstanceInfo}
        @raise PythonApiException: If host was not yet provisioned
        """
        if self.get_state() == "DEFINED":
            raise PythonApiException("Host must first be provision(ed|ing)")

        info_json = self._api.get_client().read("hosts/" + self.get_uuid() + "/VM/state")
        return InstanceInfo(info_json)

    def get_identifier(self):
        """
        Provides host's identifier. The identifier is actually a path including
        the names of host's organization and environment. In path 'org/env/host',
        'org' is the name of the organization, 'env' the name of the environment
        and 'host' the name of the 'host'. Note that 'org/env' is the identifier
        of environment 'env'.
        @return: Host's identifier
        @rtype: String
        """
        env_uuid = self.get_environment()
        env = self._api.get_environment_collection().get_resource(env_uuid)
        return env.get_identifier() + "/" + self.get_name()

    def _show(self, indent = 0):
        print " "*indent, "UUID:", self.get_uuid()
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

    def show_properties(self, indent = 0):
        """
        Prints Host's properties to standard output in a user-friendly way.
        
        @param indent: The number of spaces to put in front of each displayed
        line.
        @type indent: Integer
        """
        print " "*indent, "Properties:"
        props = self.get_properties()
        for p in props:
            p.show(indent + 2)
            print

    def provision(self):
        """
        Provisions host.
        @raise PythonApiException: If host could not be provisioned.
        """
        uuid = self.get_uuid()
        client = self._api.get_client()
        try:
            client.update("provisioner/_provision",
                      parameters = {"hostId":uuid}, decode = False)
        except ApiException, e:
            raise PythonApiException("Unable to provision host: " + e.message)

    def start(self):
        """
        Starts host.
        @raise PythonApiException: If host could not be started.
        """
        result = self._api.get_client().update("hosts/" + self.get_uuid() + "/VM/_start", decode = False)
        if(result.getcode() != 202):
            raise PythonApiException("Call not accepted by server")

    def pause(self):
        """
        Pauses host.
        @raise PythonApiException: If host could not be paused.
        """
        result = self._api.get_client().update("hosts/" + self.get_uuid() + "/VM/_pause", decode = False)
        if(result.getcode() != 202):
            raise PythonApiException("Call not accepted by server")

    def resume(self):
        """
        Resumes host's execution (after pause).
        @raise PythonApiException: If host's execution could not be resumed.
        """
        result = self._api.get_client().update("hosts/" + self.get_uuid() + "/VM/_resume", decode = False)
        if(result.getcode() != 202):
            raise PythonApiException("Call not accepted by server")

    def shutdown(self):
        """
        Shutdowns host.
        @raise PythonApiException: If host could not be shutdown.
        """
        result = self._api.get_client().update("hosts/" + self.get_uuid() + "/VM/_stop", decode = False)
        if(result.getcode() != 202):
            raise PythonApiException("Call not accepted by server")

    def poweroff(self):
        """
        Power-off host.
        @raise PythonApiException: If host could not be powered-off.
        """
        try:
            result = self._api.get_client().update("hosts/" + self.get_uuid() + "/VM/_off", decode = False)
            if(result.getcode() != 202):
                raise PythonApiException("Call not accepted by server")
        except ApiException, e:
            raise PythonApiException("Unable to poweroff host: " + e.message)
