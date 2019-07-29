# coding: utf-8
"""
Provides classes related to setting entities, in particular L{HasSettings}.
"""
from __future__ import print_function

from comodit_client.api.entity import Entity
from comodit_client.api.collection import Collection
from comodit_client.util.json_wrapper import JsonWrapper


class Schema(JsonWrapper):

    @property
    def multiline(self):
        return self._get_field("multiline")

    @property
    def schema_type(self):
        return self._get_field("type")

    
    @property
    def secret(self):
        return self._get_field("secret")

    @property
    def final(self):
        return self._get_field("final")
    
    def _show(self, indent = 0):
        print(" "*indent, "Type:", self.schema_type)
        print(" "*indent, "Multiline:", self.multiline)
        print(" "*indent, "Final:", self.final)
        print(" "*indent, "Secret:", self.secret)

class Setting(Entity):
    """
    Base class for all setting representations.
    """

    @property
    def identifier(self):
        return self.key

    @property
    def name(self):
        return self.key

    @property
    def key(self):
        """
        Setting's key.

        @rtype: string
        """

        return self._get_field("key")

    @key.setter
    def key(self, key):
        self._set_field("key", key)

    @property
    def value(self):
        """
        Setting's host.

        @rtype: string
        """

        return self._get_field("value")

    @property
    def schema(self):
        return Schema(self._get_field("schema"))

    def _show(self, indent = 0, schema=True):
        print(" "*indent, "Key:", self.key)
        print(" "*indent, "Value:", self.value)
        if schema:
            print(" "*indent, "Schema:")
            self.schema._show(indent + 2)


class SimpleSetting(Setting):
    """
    Simple setting representation. A simple setting has a value directly set
    by the user.
    """

    @property
    def value(self):
        """
        Setting's value.

        @rtype: JSON object
        """

        return self._get_field("value")

    @value.setter
    def value(self, value):
        """
        Sets setting's value.

        @param value: Setting's new value.
        @type value: JSON object
        """

        self._set_field("value", value)

    @value.deleter
    def del_value(self):
        """
        Clears value.
        """

        self._del_field("value")

    def _show(self, indent = 0):
        super(SimpleSetting, self)._show(indent)
        print(" "*indent, "Value:", self.value)

class LinkSetting(Setting):
    """
    Link setting representation. A link setting has a value that depends of
    target setting. A default value can be defined, so the setting has
    a valid value when target does not exist.
    """

    @property
    def link(self):
        """
        Targeted setting. A path-like notation is used to define a link. For
        instance, the link to setting having key 'k' in organization 'o' is given
        by 'organizations/o/settings/k'.

        @rtype: string
        """

        return self._get_field("link")

    @link.setter
    def link(self, link):
        """
        Sets link to target setting.

        @param link: Path to target setting.
        @type link: string
        """

        self._set_field("link", link)

    @property
    def default(self):
        """
        The default value of the setting.

        @rtype: JSON object
        """

        return self._get_field("value")

    @default.setter
    def default(self, default):
        """
        Sets the default value of the setting.
        
        @param default: Default value.
        @type default: JSON object
        """

        self._set_field("value", default)

    def _show(self, indent = 0):
        super(LinkSetting, self)._show(indent)
        print(" "*indent, "Link:", self.link)
        print(" "*indent, "Default value:", self.default)


class PropertySetting(Setting):
    """
    Property setting representation. A property setting has a value that depends
    on the value of host instance's property (see L{Property}).
    """

    @property
    def property_f(self):
        """
        Property key.

        @rtype: string
        """

        return self._get_field("property")

    @property_f.setter
    def property_f(self, prop):
        """
        Sets property key.

        @param prop: Property's key.
        @type prop: string
        """

        self._set_field("property", prop)

    @property_f.deleter
    def del_property_f(self, prop):
        """
        Clears property key.
        """

        self._del_field("property")

    def _show(self, indent = 0):
        super(PropertySetting, self)._show(indent)
        print(" "*indent, "Property:", self.property_f)


def _build_setting(collection, json_data):
    if not json_data:
        return SimpleSetting(collection, json_data)

    has_prop = "property" in json_data and json_data["property"]
    has_link = "link" in json_data and json_data["link"]

    if has_prop and not has_link:
        return PropertySetting(collection, json_data)
    elif not has_prop and has_link:
        return LinkSetting(collection, json_data)
    else:
        return SimpleSetting(collection, json_data)

class SettingImpact(Entity):

    @property
    def settingHandlerContexts(self):
        """
        List of setting with handler.

        @rtype: list of settingHandlerContexts L{SettingHandlerContext}
        """

        return self._get_list_field("settingHandlerContexts", lambda x: SettingHandlerContext(x))

    @settingHandlerContexts.setter
    def argumsettingHandlerContextsents(self, settingHandlerContexts):
        """
        Sets list of setting with handler.

        @param groups: New list of setting with handler.
        @type groups: list of SettingHandlerContext
        """

        return self._set_list_field("settingHandlerContexts", settingHandlerContexts)


    @property
    def otherResources(self):
        """
        Sets list of setting without handler.

        @param groups: New list of setting without handler.
        @type groups: list of String
        """
        return self._get_list_field("otherResources")

    @otherResources.setter
    def otherResources(self, otherResources):
        """
        Sets list of setting without handler.

        @param groups: New list of setting without handler.
        @type groups: list of String
        """
        return self._set_list_field("otherResources", otherResources)

    def show(self, indent = 0):
        print(" "*(indent + 2), "Resources automatically updated by event handlers")
        for s in self.settingHandlerContexts:
            s.show(2)

        print(" "*(indent + 2), "Other impacted resources without event handler")
        for g in self.otherResources:
            print(" "*(indent + 4), g)

class SettingImpactCollection(Collection):

     def _new(self, json_data = None):
        return SettingImpact(self, json_data)

class OrganizationSettingTree(JsonWrapper):

    @property
    def organization(self):
        """
        Organization name

        @rtype: string
        """

        return self._get_field("organization")

    @property
    def settings(self):
        """
        Setting's organization.

        @rtype: Setting
        """

        return self._get_list_field("settings", lambda x: Setting(None, x))

    @property
    def environments(self):
        """
        environment's organization.

        @rtype: EnvironmentSettingTree
        """

        return self._get_list_field("environments", lambda x: EnvironmentSettingTree(x))

    @property
    def distributions(self):
        """
        distribution's organization.

        @rtype: DistributiontSettingTree
        """

        return self._get_list_field("distributions", lambda x: DistributionSettingTree(x))

    @property
    def platforms(self):
        """
        platform's organization.

        @rtype: PlatformSettingTree
        """

        return self._get_list_field("platforms", lambda x: PlatformSettingTree(x))
    
    @property
    def environments(self):
        """
        environment's organization.

        @rtype: EnvironmentSettingTree
        """

        return self._get_list_field("environments", lambda x: EnvironmentSettingTree(x))

    def show(self, indent=0):
        print(" "*(indent + 2), "Organization:", self.organization)
        
        print(" "*(indent + 2), "Settings:")
        for s in self.settings:
            s._show(indent + 4, False)
        
        print(" "*(indent + 2), "Environments:")
        for e in self.environments:
            e._show(indent + 4)

        print(" "*(indent + 2), "Distributions:")
        for e in self.distributions:
            e._show(indent + 4)

        print(" "*(indent + 2), "Platforms:")
        for e in self.platforms:
            e._show(indent + 4)


class EnvironmentSettingTree(JsonWrapper):

    @property
    def environment(self):
        """
        Environment name.

        @rtype: string
        """

        return self._get_field("environment")

    @property
    def settings(self):
        """
        Setting's environment.

        @rtype: Setting
        """

        return self._get_list_field("settings", lambda x: Setting(None, x))

    @property
    def hosts(self):
        """
        host's environment.

        @rtype: HostSettingTree
        """

        return self._get_list_field("hosts", lambda x: HostSettingTree(x))

    
    def _show(self, indent=2):
        print(" "*(indent + 2), "Environment:", self.environment)
        print(" "*(indent + 2), "Settings:")
        for s in self.settings:
            s._show(indent + 4, False)

        print(" "*(indent + 2), "Hosts:")
        for h in self.hosts:
            h._show(indent + 4)

class DistributionSettingTree(JsonWrapper):

    @property
    def distribution(self):
        """
        distribution name.

        @rtype: string
        """

        return self._get_field("distribution")

    @property
    def settings(self):
        """
        Setting's distribution.

        @rtype: Setting
        """

        return self._get_list_field("settings", lambda x: Setting(None, x))

    def _show(self, indent=2):
        print(" "*(indent + 2), "Distribution:", self.distribution)
        print(" "*(indent + 2), "Settings:")
        for s in self.settings:
            s._show(indent + 4, False)

class PlatformSettingTree(JsonWrapper):

    @property
    def platform(self):
        """
        Platform name.

        @rtype: string
        """

        return self._get_field("platform")

    @property
    def settings(self):
        """
        Setting's platform.

        @rtype: Setting
        """

        return self._get_list_field("settings", lambda x: Setting(None, x))

    def _show(self, indent=2):
        print(" "*(indent + 2), "Platform:", self.platform)
        print(" "*(indent + 2), "Settings:")
        for s in self.settings:
            s._show(indent + 4, False)

class HostSettingTree(JsonWrapper):

    @property
    def host(self):
        """
        Host name.

        @rtype: string
        """

        return self._get_field("host")

    @property
    def settings(self):
        """
        Setting's host.

        @rtype: Setting
        """

        return self._get_list_field("settings", lambda x: Setting(None, x))

    @property
    def applications(self):
        """
        applications's host.

        @rtype: ApplicationSettingTree
        """

        return self._get_list_field("applications", lambda x: ApplicationSettingTree(x))

    @property
    def distribution(self):
        """
        distribution's host.

        @rtype: DistributionSettingTree
        """

        return DistributionSettingTree(self._get_field("distribution"))

    
    def _show(self, indent=2):
        print(" "*(indent + 2), "Host:", self.host)
        print(" "*(indent + 2), "Settings:")
        
        for s in self.settings:
            s._show(indent + 4, False)

        if self.applications:
            print(" "*(indent + 2), "Applications:")
            for a in self.applications:
                a._show(indent + 4)


class ApplicationSettingTree(JsonWrapper):

    @property
    def application(self):
        """
        Application name.

        @rtype: string
        """

        return self._get_field("application")

    @property
    def settings(self):
        """
        Setting's ApplicationContext.

        @rtype: Setting
        """

        return self._get_list_field("settings", lambda x :Setting(None, x))

    def _show(self, indent=2):
        print(" "*(indent + 2), "Application:", self.application)
        print(" "*(indent + 2), "Settings:")
        for s in self.settings:
            s._show(indent + 4, False)
        


class SettingHandlerContext(JsonWrapper):
    @property
    def application(self):
        """
        application name

        @rtype: String
        """
        return self._get_field("application")
    
    @application.setter
    def application(self, application):
        """
        Sets application name.
        """

        self._set_field("application", application.get_json())

    @property
    def hosts(self):
        """
        List of hosts with handler or setting isn't define

        @rtype: list of hosts L{HostSettingContext}
        """

        return self._get_list_field("hosts", lambda x: HostSettingContext(x))

    @hosts.setter
    def hosts(self, hosts):
        """
        Sets list of hosts with handler or setting isn't define

        @param groups: New list of hosts.
        @type groups: list of HostSettingContext
        """
        return self._set_list_field("hosts", hosts)

    @property
    def handlers(self):
        """
        List of handler

        @rtype: list of handlers L{HandlerSettingContext}
        """

        return self._get_list_field("handlers", lambda x: HandlerSettingContext(x))

    @handlers.setter
    def handlers(self, handlers):
        """
        Sets list of handler

        @param groups: New list of handler
        @type groups: list of HandlerSettingContext
        """
        return self._set_list_field("handlers", handlers)

    def show(self, indent = 0):
        print(" "*(indent + 2), "application", self.application)
        indent += 2
        print(" "*(indent + 2), "Hosts")
        for h in self.hosts:
            h.show(indent)
        print(" "*(indent + 2), "Actions")
        for h in self.handlers:
            h.show(indent)

class HostSettingContext(JsonWrapper):
    @property
    def name(self):
        """
        name of host

        @rtype: String
        """
        return self._get_field("name")
    
    @name.setter
    def name(self, name):
        """
        Sets name of host
        """

        self._set_field("name", name.get_json())
        
    @property
    def environment(self):
        """
        name of environment where is host

        @rtype: String
        """
        return self._get_field("environment")
    
    @environment.setter
    def environment(self, environment):
        """
        Sets name of environment
        """

        self._set_field("environment", environment.get_json())

    def show(self, indent = 0):        
        print(" "*(indent + 4), self.environment + "\\" + self.name)

class HandlerSettingContext(JsonWrapper):
    @property
    def do(self):
        """
        List of actions on Handler.

        @rtype: list of actions L{Do}
        """

        return self._get_list_field("do", lambda x: Do(x))

    @do.setter
    def do(self, handlers):
        """
        Sets list of action

        @param groups: New list of action.
        @type groups: list of Do
        """
        return self._set_list_field("do", do)

    def show(self, indent = 0):
        for d in self.do:
            d.show(indent + 2)

class Do(JsonWrapper):
    @property
    def action(self):
        """
        action to do on ressource

        @rtype: String
        """
        return self._get_field("action")
    
    @action.setter
    def action(self, action):
        """
        Sets action
        """

        self._set_field("action", action.get_json())
        
    @property
    def resource(self):
        """
        resource name

        @rtype: String
        """
        return self._get_field("resource")
    
    @resource.setter
    def resource(self, resource):
        """
        Sets resource name

        @rtype: String
        """

        self._set_field("resource", resource.get_json())

    def show(self, indent = 0):
        print(" "*(indent + 2), self.action, self.resource)



class SettingCollection(Collection):
    """
    Collection of L{settings<Setting>}.
    """

    def _new(self, json_data = None):
        return _build_setting(self, json_data)

    def _new_simple(self, json_data = None):
        return SimpleSetting(self, json_data)

    def _new_link(self, json_data = None):
        return LinkSetting(self, json_data)

    def _new_property(self, json_data = None):
        return PropertySetting(self, json_data)

    def new_simple(self, key, value):
        """
        Instantiates a new simple setting.

        @param key: setting's key.
        @type key: string
        @param value: setting's value.
        @type value: JSON object
        @return: a new simple setting.
        @rtype: L{SimpleSetting}
        """

        s = self._new_simple()
        s.key = key
        s.value = value
        return s

    def new_link(self, key, link, default):
        """
        Instantiates a new link setting.

        @param key: setting's key.
        @type key: string
        @param link: setting's link.
        @type link: string
        @param default: setting's default value.
        @type default: JSON object
        @return: a new link setting.
        @rtype: L{LinkSetting}
        """

        s = self._new_link()
        s.key = key
        s.link = link
        s.default = default
        return s

    def new_property(self, key, prop):
        """
        Instantiates a new link setting.

        @param key: setting's key.
        @type key: string
        @param prop: setting's property.
        @type prop: string
        @return: a new property setting.
        @rtype: L{PropertySetting}
        """

        s = self._new_property()
        s.key = key
        s.property_f = prop
        return s

    def update(self, key, new_val):
        """
        Updates the value of a remote simple setting.
        
        @param key: Setting's key.
        @type key: string
        @param new_val: New setting value.
        @type new_val: JSON object
        @return: Updated setting.
        @rtype: L{SimpleSetting}
        """

        s = self.get(key)
        s.value = new_val
        s.update()
        return s

    def create(self, key, value):
        """
        A call to this method is equivalent to C{create_simple(key, value)}.

        @return: New setting's representation.
        @rtype: L{SimpleSetting}
        """

        return self.create_simple(key, value)

    def create_simple(self, key, value):
        """
        Creates a remote simple setting.

        @param key: setting's key.
        @type key: string
        @param value: setting's value.
        @type value: JSON object
        @return: a new simple setting.
        @rtype: L{SimpleSetting}
        """

        setting = self.new_simple(key, value)
        setting.create()
        return setting

    def create_link(self, key, link, default):
        """
        Creates a remote link setting.

        @param key: setting's key.
        @type key: string
        @param link: setting's link.
        @type link: string
        @param default: setting's default value.
        @type default: JSON object
        @return: a new link setting.
        @rtype: L{LinkSetting}
        """

        setting = self.new_link(key, link, default)
        setting.create()
        return setting

    def create_property(self, key, prop):
        """
        Creates a remote property setting.

        @param key: setting's key.
        @type key: string
        @param prop: setting's property.
        @type prop: string
        @return: a new property setting.
        @rtype: L{PropertySetting}
        """

        setting = self.new_property(key, prop)
        setting.create()
        return setting

    def get_as_link(self, key):
        """
        Fetches a setting and converts it into a link setting.

        @param key: Setting's key.
        @type key: string
        @return: A link setting.
        @rtype: L{LinkSetting}
        """

        s = self.get(key)
        data = s.get_json()
        data.pop("property", "")
        return LinkSetting(self, data)

    def change(self, settings, no_delete = False):
        """
        @param settings: the new settings list
        @type settings: List of L{Setting}
        """

        data = {
            'newOrUpdatedSettings': [setting.get_json() for setting in settings]
        }
        parameters = {
            'no_delete': "true" if no_delete else "false"
        }
        self.client._http_client.update(self.url, data, parameters=parameters)


class HasSettings(Entity):
    """
    Super class for entities having settings.
    """

    def settings(self):
        """
        Instantiates settings collection.

        @return: Settings collection.
        @rtype: L{SettingCollection}
        """

        return SettingCollection(self.client, self.url + "settings/")

    def tree(self, secret=False, no_secret=False, key=None):
        """
        Get where setting is defined on each level

        @return: organizationSettingTree.
        @rtype: L{OrganizationSettingTree}
        """
        parameters = {};
        parameters["secret_only"] = secret
        parameters["no_secret"] = no_secret
        if key:
            parameters["key"] = key        

        json = self.client._http_client.read(self.url+ "tree/settings/", parameters=parameters)
        return OrganizationSettingTree(json)

    def add_setting(self, key, value):
        self.add_simple_setting(key, value)

    def impact(self, key):
        return SettingImpactCollection(self.client, self.url + "settings/" + key ).get("/impact")
        
    def add_simple_setting(self, key, value):
        """
        Adds a simple setting to local list of settings. Note that this list is considered only at creation time.
        For later modifications, collection must be used.

        @param key: The setting's key.
        @type key: string
        """

        setting = self.settings().new_simple(key, value)
        self._add_to_list_field("settings", setting)

    def add_link_setting(self, key, link, default):
        """
        Adds a link setting to local list of settings. Note that this list is considered only at creation time.
        For later modifications, collection must be used.

        @param key: The setting's key.
        @type key: string
        """

        setting = self.settings().new_link(key, link, default)
        self._add_to_list_field("settings", setting)

    def add_property_setting(self, key, prop):
        """
        Adds a property setting to local list of settings. Note that this list is considered only at creation time.
        For later modifications, collection must be used.

        @param key: The setting's key.
        @type key: string
        """

        setting = self.settings().new_property(key, prop)
        self._add_to_list_field("settings", setting)

    def get_setting(self, key):
        """
        Fetches a setting.
        
        @param key: The setting's key.
        @type key: string
        @return: The setting.
        @rtype: L{Setting}
        """

        return self.settings().get(key)

    @property
    def settings_f(self):
        """
        The local list of settings.

        @rtype: list of L{Setting}
        """

        return self._get_list_field("settings", lambda x: _build_setting(self.settings(), x))

    @settings_f.setter
    def settings_f(self, settings):
        """
        Sets the local list of settings. Note that this list is considered only at creation time.
        For later modifications, collection must be used.

        @param settings: The new list of settings.
        @type settings: list of L{Setting}
        """

        self._set_list_field("settings", settings)

    def _show_settings(self, indent = 0):
        print(" "*indent, "Settings:")
        for s in self.settings_f:
            s._show(indent + 2)

def add_settings(container, settings):
    """
    Helper function that adds simple settings taken from a dictionary to a
    container.

    @param container: The container.
    @type container: L{HasSettings}
    @param settings: The dictionary containing settings' data. Each key is
    interpreted as a setting key and each value as simple setting value.
    @type settings: dict
    """

    for key, value in settings.items():
        container.add_simple_setting(key, value)
