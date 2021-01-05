# coding: utf-8
"""
Provides the classes related to job entity: L{Webhook}
and L{WebhookCollection}.
"""
from __future__ import print_function
from __future__ import absolute_import

from .collection import Collection
from comodit_client.api.entity import Entity
from comodit_client.util.json_wrapper import JsonWrapper
from comodit_client.api.exceptions import PythonApiException
from comodit_client.rest.exceptions import ApiException


class WebhookCollection(Collection):
    """
        Collection of webhooks. A webhook collection is owned by an organization
        L{Organization}.
        """

    def _new(self, json_data=None):
        return Webhook(self, json_data)

    def new(self, name, description=""):
        """
        Instantiates a new webhook object.

        @param name: The name of new webhook.
        @type name: string
        @param description: The description of new webhook.
        @type description: string
        @rtype: L{Webhook}
        """

        webhook = self._new()
        webhook.name = name
        webhook.description = description
        return webhook

    def create(self, name, description=""):
        """
        Creates a remote webhook entity and returns associated local
        object.

        @param name: The name of new webhook.
        @type name: string
        @param description: The description of new webhook.
        @type description: string
        @rtype: L{Webhook}
        """

        webhook = self.new(name, description)
        webhook.create()
        return webhook

class Webhook(Entity):
    """
    Webhook entity representation. A Webhook is an object to send rest request

    """
    @property
    def organization(self):
        """
        The name of the organization owning this orchestration.

        @rtype: string
        """

        return self._get_field("organization")

    @property
    def server_name(self):
        """
        Server name or IP

        @rtype: string
        """
        return self._get_field("serverName")

    @property
    def path(self):
        """
        path of request

        @rtype: string
        """
        return self._get_field("path")

    @property
    def protocol(self):
        """
        Protocol for request. Can be :
        HTTP, HTTPS

        @rtype: string
        """
        return self._get_field("protocol")

    @property
    def method(self):
        """
        Method for request. Can be :
        GET, POST, PUT, DELETE

        @rtype: string
        """
        return self._get_field("method")

    @property
    def port(self):
        """
        Port to send request

        @rtype: int
        """
        return self._get_field("port")


    @property
    def authentication_method(self):
        """
        Authentication method for request. Can be :
        NO_AUTH, BASIC_AUTH

        @rtype: string
        """
        return self._get_field("authenticationMethod")

    @property
    def username(self):
        """
        username for basic_auth

        @rtype: string
        """
        return self._get_field("username")


    @property
    def token(self):
        """
        password for basic_auth

        @rtype: string
        """
        return self._get_field("token")

    @property
    def body(self):
        """
        body of request

        @rtype: string
        """
        return self._get_field("body")

    @property
    def headers(self):
        """
        List of headers

        @rtype: list of headers L{WebhookParameter}
        """

        return self._get_list_field("headers", lambda x: WebhookParameter(x))

    @property
    def parameters(self):
        """
        List of parameters

        @rtype: list of parameters L{WebhookParameter}
        """

        return self._get_list_field("parameters", lambda x: WebhookParameter(x))

    @property
    def properties(self):
        """
        List of properties : jsonpath to extract from result of request

        @rtype: list of parameters L{WebhookParameter}
        """

        return self._get_list_field("properties", lambda x: WebhookProperty(x))

    def impact(self, indent = 0):
        print(" "*indent, "Method:", self.method)
        print(" "*indent, "ServerName:", self.server_name)
        print(" "*indent, "Path:", self.path)

        print(" " * indent, "Properties:")
        for p in self.properties:
            p._show(indent + 2)

    def _show(self, indent = 0):
        print(" "*indent, "Name:", self.name)
        print(" "*indent, "Description:", self.description)
        print(" "*indent, "Organization:", self.organization)
        print(" "*indent, "Authentication method:", self.authentication_method)
        if self.username is not None:
            print(" " *indent, "Username:", self.username)
        if self.token is not None:
            print(" "*indent, "Token:", self.token)
        print(" "*indent, "Protocol:", self.protocol)
        print(" "*indent, "Server name:", self.server_name)
        print(" "*indent, "Port:", self.port)
        print(" "*indent, "path:", self.path)

        print(" "*indent, "Headers:")
        for h in self.headers:
            h._show(indent + 2)

        print(" "*indent, "Parameters:")
        for p in self.parameters:
            p._show(indent + 2)

        print(" " * indent, "body:", self.body)

        print(" " * indent, "Properties:")
        for p in self.properties:
            p._show(indent + 2)

    def run(self):
        """
        Requests to run webhook

        @return: WebhookResult
        @rtype: L{WebhookResult}
        """
        result  = self._http_client.update(self.url + "_run")
        return WebhookResult(result)


class WebhookParameter(JsonWrapper):

    @property
    def name(self):
        """
        Name of parameter.

        @rtype: string
        """

        return self._get_field("name")

    @property
    def value(self):
        """
        Value of parameter.

        @rtype: string
        """

        return self._get_field("value")

    @property
    def secret(self):
        """
        Parameter is secret or not.

        @rtype: boolean
        """

        return self._get_field("secret")

    def _show(self, indent = 0):
        print(" "*indent, "Name:", self.name)
        print(" "*indent, "Value:", self.value)
        print(" "*indent, "Secret:", self.secret)

class WebhookProperty(JsonWrapper):

    @property
    def name(self):
        """
        Name property.

        @rtype: string
        """

        return self._get_field("name")

    @property
    def json_path(self):
        """
        jsonPath to extract from result

        @rtype: string
        """

        return self._get_field("jsonPath")

    def _show(self, indent = 0):
        print(" "*indent, "Name:", self.name)
        print(" "*indent, "Value:", self.json_path)


class WebhookResult(JsonWrapper):

    @property
    def return_code(self):
        """
        Result code of rest request

        @rtype: int
        """

        return self._get_field("returnCode")

    @property
    def properties(self):
        """
        List of properties : jsonpath extracted from result of rest request

        @rtype: list of parameters L{PropertyResult}
        """

        return self._get_list_field("properties", lambda x: PropertyResult(x))

    def show(self, indent = 0):
        print(" "*indent, "Return code:", self.return_code)
        print(" " * indent, "Properties:")
        for p in self.properties:
            p._show(indent + 2)


class PropertyResult(JsonWrapper):

    @property
    def name(self):
        """
        Name of property.

        @rtype: string
        """

        return self._get_field("name")

    @property
    def value(self):
        """
        value of property.

        @rtype: string
        """

        return self._get_field("value")

    def _show(self, indent = 0):
        print(" "*indent, "Name:", self.name)
        print(" "*indent, "Value:", self.value)
