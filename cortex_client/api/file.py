# coding: utf-8
"""
File module.

@organization: Guardis
@copyright: 2011 Guardis SPRL, Liège, Belgium.
"""

from cortex_client.util.json_wrapper import JsonWrapper

class Parameter(JsonWrapper):
    """
    A template's parameter. A parameter is reprensented by a key, a default value
    and a name. A version is also associated to the parameter by the server.
    """
    def __init__(self, json_data = None):
        super(Parameter, self).__init__(json_data)

    def get_key(self):
        """
        Provides parameter's key.
        @return: The key
        @rtype: String
        """
        return self._get_field("key")

    def set_key(self, key):
        """
        Sets parameter's key.
        @param key: The key
        @type key: String
        """
        return self._set_field("key", key)

    def get_value(self):
        """
        Provides parameter's default value.
        @return: The default value
        @rtype: String
        """
        return self._get_field("value")

    def set_value(self, value):
        """
        Sets parameter's default value.
        @param value: The default value
        @type value: String
        """
        return self._set_field("value", value)

    def get_name(self):
        """
        Provides parameter's name.
        @return: The name
        @rtype: String
        """
        return self._get_field("name")

    def set_name(self, name):
        """
        Sets parameter's name.
        @param name: The name
        @type name: String
        """
        return self._set_field("name", name)

    def get_version(self):
        """
        Provides parameter's version number.
        @return: The version number
        @rtype: Integer
        """
        return int(self._get_field("version"))

    def show(self, indent = 0):
        """
        Prints parameter's state to standard output in a user-friendly way.
        
        @param indent: The number of spaces to put in front of each displayed
        line.
        @type indent: Integer
        """
        print " "*indent, "Key:", self.get_key()
        print " "*indent, "Value:", self.get_value()


class ParameterFactory(object):
    """
    File parameter factory.
    
    @see: L{Parameter}
    @see: L{cortex_client.util.json_wrapper.JsonWrapper._get_list_field}
    """
    def new_object(self, json_data):
        """
        Instantiates a L{Parameter} object using given state.
        
        @param json_data: A quasi-JSON representation of a Package instance's state.
        @type json_data: String, dict or list
        
        @return: A parameter
        @rtype: L{Parameter}
        """
        return Parameter(json_data)


class File(JsonWrapper):
    """
    A file template. A template is the representation of a parametrized file.
    A template may be rendered after values are given to its parameters (see
    L{RenderingService}).
    """
    def __init__(self, json_data = None):
        """
        @param api: An access point.
        @type api: L{CortexApi}
        @param json_data: A quasi-JSON representation of application's state.
        @type json_data: dict, list or String
        """
        super(File, self).__init__(json_data)

    def get_name(self):
        """
        Provides the name of this resource or None if it is not yet set.
        
        @return: The name of this resource.
        @rtype: String
        """
        return self._get_field("name")

    def set_name(self, name):
        """
        Sets the name of this resource.

        @param name: The new name
        @type name: String
        """
        self._set_field("name", name)

    def get_parameters(self):
        """
        Provides the list of parameters associated to this template.
        @return: The list of parameters
        @rtype: list of L{Parameter}
        """
        return self._get_list_field("parameters", ParameterFactory())

    def set_parameters(self, parameters):
        """
        Sets the list of parameters associated to this template.
        @param parameters: The list of parameters
        @type parameters: list of L{Parameter}
        """
        self._set_list_field("parameters", parameters)

    def add_parameter(self, parameter):
        """
        Adds a parameter to the list of parameters associated to this template.
        @param parameter: The parameter
        @type parameter: L{Parameter}
        """
        self._add_to_list_field("parameters", parameter)

    def show(self, indent = 0):
        print " "*indent, "Name:", self.get_name()
        print " "*indent, "Parameters:"
        parameters = self.get_parameters()
        for p in parameters:
            p.show(indent + 2)
