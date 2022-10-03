# coding: utf-8
"""
Provides the classes related to applicationResourceProperty entity: L{ApplicationResourceProperty}
and L{ApplicationResourcePropertyCollection}.
"""
from __future__ import print_function
from __future__ import absolute_import

from .collection import Collection
from comodit_client.api.entity import Entity


class ApplicationResourcePropertyCollection(Collection):
    """
    Collection of jobs. A job collection is owned by an organization
    L{Organization}.
    """

    def _new(self, json_data=None):
        return ApplicationResourceProperty(self, json_data)

    def new(self, name):
        """
        Instantiates a new ApplicationResourceProperty object.

        @param name: The name of new applicationResourceProperty.
        @type name: string
        @param description: The description of new job.
        @type description: string
        @rtype: L{Job}
        """

        application_resource_property = self._new()
        application_resource_property.name = name
        return application_resource_property

    def create(self, name):
        """
        Creates a remote job entity and returns associated local
        object.

        @param name: The name of new application_resource_property.
        @type name: string
        @type description: string
        @rtype: L{Job}
        """

        application_resource_property = self.new(name)
        application_resource_property.create()
        return application_resource_property


class ApplicationResourceProperty(Entity):
    """
    Job entity representation. A job is an action to execute on host, settings. It's
    possible to execute a job at Date or by cron.

    """

    @property
    def organization(self):
        """
        The name of the organization owning this.

        @rtype: string
        """
        return self._get_field("organization")

    @property
    def identifier(self):
        return self._get_field("id")

    @property
    def name(self):
        return self.identifier

    @property
    def environment(self):
        """
        The name of the environment owning this.

        @rtype: string
        """
        return self._get_field("environment")

    @property
    def application(self):
        """
        The name of the application owning this.

        @rtype: string
        """
        return self._get_field("application")

    @application.setter
    def application(self, application):
        """
        Sets the name of the application owning this.

        @type name: string
        """

        self._set_field("application", application)

    @property
    def host_group(self):
        """
        The name of the host group owning this job.

        @rtype: string
        """
        return self._get_field("hostGroup")

    @property
    def host(self):
        """
        The name of the host owning this.

        @rtype: string
        """
        return self._get_field("host")

    @property
    def application_context(self):
        """
        The name of the application_context owning this.

        @rtype: string
        """
        return self._get_field("applicationContext")

    @property
    def key(self):
        """
        The resource key of this.

        @rtype: string
        """
        return self._get_field("key")

    @key.setter
    def key(self, key):
        """
        Sets the resource key of this.

        @type name: string
        """

        self._set_field("key", key)


    @property
    def value(self):
        """
        The value of this

        @rtype: string
        """
        return self._get_field("value")

    @property
    def package_name(self):
        """
        The name of the package owning this.

        @rtype: string
        """
        return self._get_field("packageName")

    @package_name.setter
    def package_name(self, package_name):
        """
        Sets the name of the package owning this.

        @type name: string
        """

        self._set_field("packageName", package_name)

    @property
    def rpm_module(self):
        """
        The name of the rpm module owning this job.

        @rtype: string
        """
        return self._get_field("rpmModule")

    @rpm_module.setter
    def rpm_module(self, rpm_module):
        """
        Sets the name of the rpm module owning this.

        @type name: string
        """

        self._set_field("rpmModule", rpm_module)

    def _show(self, indent=0):
        print(" " * indent, "Key:", self.identifier)
        print(" " * indent, "Value:", self.value)

    def update(self, force=False):
        parameters = {}
        if force:
            parameters["force"] = "true"
        return self.client._http_client.update(self.collection.url + self.key,
                                               self.get_json(),
                                               parameters=parameters)

    def create(self, parameters={}):
        return self.client._http_client.create(self.getUrl(), self.get_json(), parameters=parameters)

    def getUrl(self):
        if self.package_name:
            url = self.collection.url + "applications/" + self.application + "/packages/" + self.package_name + "/properties/" + self.key
        elif self.rpm_module:
            url = self.collection.url + "applications/" + self.application + "/rpmmodules/" + self.rpm_module + "/properties/" + self.key
        return url

    def delete(self, parameters = {}):
        """
        Deletes associated remote entity from the server.

        @raise PythonApiException: If collection is not set.
        """
        self._http_client.delete(self.collection.url + self.key, parameters = parameters)
