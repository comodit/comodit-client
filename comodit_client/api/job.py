# coding: utf-8
"""
Provides the classes related to job entity: L{Job}
and L{JobCollection}.
"""
from __future__ import print_function
from __future__ import absolute_import

from .collection import Collection
from comodit_client.api.entity import Entity
from comodit_client.util.json_wrapper import JsonWrapper
from comodit_client.api.exceptions import PythonApiException
from comodit_client.rest.exceptions import ApiException



class JobCollection(Collection):
    """
    Collection of jobs. A job collection is owned by an organization
    L{Organization}.
    """

    def _new(self, json_data = None):
        return Job(self, json_data)

    def new(self, name, description = ""):
        """
        Instantiates a new job object.

        @param name: The name of new job.
        @type name: string
        @param description: The description of new job.
        @type description: string
        @rtype: L{Job}
        """

        job = self._new()
        job.name = name
        job.description = description
        return job

    def create(self, name, description = ""):
        """
        Creates a remote job entity and returns associated local
        object.

        @param name: The name of new job.
        @type name: string
        @param description: The description of new job.
        @type description: string
        @rtype: L{Job}
        """

        job = self.new(name, description)
        job.create()
        return job

class Job(Entity):
    """
    Job entity representation. A job is an action to execute on host, settings. It's
    possible to execute a job at Date or by cron.

    """

    @property
    def organization(self):
        """
        The name of the organization owning this job.

        @rtype: string
        """

        return self._get_field("organization")
    
    @property
    def cron(self):
        """
        The cron of job.

        @rtype: string
        """

        return self._get_field("cron")
    
    @property
    def date(self):
        """
        The execution date of job.

        @rtype: string
        """

        return self._get_field("date")
    
    @property
    def action(self):
        """
        The action of job.

        @rtype: string
        """

        return self._get_field("action")
    
    @property
    def enabled(self):
        """
        if job is active.

        @rtype: boolean
        """

        return self._get_field("enabled")

    @property
    def operation(self):
        """
        operation to apply

        @rtype: Operation
        """

        return Operation(self._get_field("operation"))

    @operation.setter
    def operation(self, operation):
        """
        Set job's operation.
        """

        self._set_field("operation", operation.get_json())

    def _show(self, indent = 0):
        print(" "*indent, "enabled:", self.enabled)
        print(" "*indent, "Name:", self.name)
        print(" "*indent, "Description:", self.description)
        print(" "*indent, "action:", self.action)
        print(" "*indent, "Organization:", self.organization)
        print(" "*indent, "cron:", self.cron)
        print(" "*indent, "date:", self.date)
        self.operation._show(indent + 2)
        
    def run(self):
        """
        Execute job
        """
        self._http_client.update(self.url + "/_run", decode = False)
        
        
class Operation(JsonWrapper):
    """
        operation of job
    """

    @property
    def description(self):
        return self._get_field("description")

    @property
    def operation(self):
        return self._get_field("operation")
    
    @property
    def arguments(self):
        """
        List of operation's arguments.

        @rtype: list of arguments L{Argument}
        """

        return self._get_list_field("arguments", lambda x: Argument(x))

    @arguments.setter
    def arguments(self, arguments):
        """
        Sets list of operation's arguments.

        @param groups: New list of job's arguments.
        @type groups: list of Arguments
        """

        return self._set_list_field("arguments", arguments)

    @operation.setter
    def operation(self, operation):
        """
        Sets job's operation.

        """

        self._set_field("operation", operation.get_json())
    
    def _show(self, indent = 0):
        print(" "*indent, "description:", self.description)
        print(" "*indent, "operation:", self.operation)
        for a in self.arguments:
            a.show(indent + 2)

class Argument(JsonWrapper):
    """
        Argument of operation
    """
    
    @property
    def description(self):
        return self._get_field("description")
    
    @description.setter
    def description(self, description):
        """
        Sets argument's description.
        """

        self._set_field("description", description.get_json())

    @property
    def type(self):
        return self._get_field("type")
    
    @type.setter
    def type(self, type):
        """
        Sets argument's type.
        """

        self._set_field("type", type.get_json())

    @property
    def value(self):
        return self._get_field("value")
    
    @value.setter
    def value(self, value):
        """
        Sets argument's value.
        """

        self._set_field("value", value.get_json())
    
    def show(self, indent = 0):
        print(" "*indent, "description:", self.description)
        print(" "*indent, "type:", self.type)
        print(" "*indent, "value:", self.value)
