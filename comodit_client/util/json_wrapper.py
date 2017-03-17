# coding: utf-8
"""
JsonWrapper class module.
"""

import json, os
from collections import OrderedDict

class JsonWrapper(object):
    """
    Wrapper around a quasi-JSON represented state. Here is an example of quasi-JSON
    representation: the string '{"key":"value"}' is actually represented by
    a dict containing one mapping of key to value where key is a string. "value"
    may be a string, another quasi-JSON representation or a list of strings or
    quasi-JSON representations.
    
    For example, string '{"field1":["a","b","c"], "field2":"value2"}' represents
    the state of an object that has 2 members, field1 and field2. Value of
    field1 is a list of strings and value of field2 a string. Note that the
    value of field2 may represent an Integer, a Boolean, etc.
    """

    def __init__(self, json_data = None):
        """
        Instantiates the class.
        
        @param json_data: A quasi-JSON representation
        @type json_data: String, dict or list
        """

        if json_data is None:
            self._json_data = {}
        else:
            self._json_data = json_data

    def _get_field(self, field, factory = None):
        """
        Returns the value of given field.

        @param field: A field name
        @type field: String
        
        @return: The quasi-JSON representation of field's value
        @rtype: String, dict or list
        """

        if factory:
            return factory(self._json_data.get(field, None))
        else:
            return self._json_data.get(field, None)

    def _set_field(self, field, value):
        """
        Sets the value of given field.

        @param field: A field name
        @type field: String
        @param value: A quasi-JSON represented value
        @type value: String, dict or list
        """

        if isinstance(value, JsonWrapper):
            self._json_data[field] = value.get_json()
        else:
            self._json_data[field] = value

    def _del_field(self, field):
        if self._json_data.has_key(field):
            del self._json_data[field]

    def _get_list_field(self, field, factory = None):
        """
        Returns the value of a field as a list of objects. Each object of the
        list is instantiated by a factory using its corresponding quasi-JSON
        representation. The factory must at least implement the method new_object
        which takes a quasi-JSON representation as argument and returns a
        Python object.

        @param field: A field name
        @type field: String
        @param factory: A factory
        @type factory: object

        @return: A list of objects
        @rtype: list of object
        """
        object_list = []
        if(self._json_data.has_key(field)):
            json_list = self._json_data[field]
            for j in json_list:
                if factory:
                    object_list.append(factory(j))
                else:
                    object_list.append(j)
        return object_list

    def _add_to_list_field(self, field, value):
        """
        Adds the quasi-JSON representation of given value to list associated
        to given field.

        @param field: A field name
        @type field: String
        @param value: A JsonWrapper instance or a String instance
        @type value: L{JsonWrapper} or String
        """
        if(not self._json_data.has_key(field)):
            self._json_data[field] = []
        if(isinstance(value, JsonWrapper)):
            self._json_data[field].append(value.get_json())
        else:
            self._json_data[field].append(value)

    def _set_list_field(self, field, object_list):
        """
        Sets the quasi-JSON representation of given object_list associated
        to given field.

        @param field: A field name
        @type field: String
        @param object_list: A list
        @type object_list: list of L{JsonWrapper} or String
        """
        json_list = []
        for o in object_list:
            if(isinstance(o, JsonWrapper)):
                json_list.append(o.get_json())
            else:
                json_list.append(o)
        self._json_data[field] = json_list

    def set_json(self, json_data):
        """
        Sets this object's state using given quasi-JSON represented value.
        
        @param json_data: A quasi-JSON represented object state.
        @type json_data: dict
        """
        if not isinstance(json_data, dict):
            raise Exception("Wrong type '" + type(json_data).__name__ + "'")
        self._json_data = json_data

    def get_json(self):
        """
        Provides the quasi-JSON representation of this object's state.
        
        @return: Quasi-representation of this object's state
        @rtype: dict
        """
        return self._json_data

    def get_real_json(self, indent = 4):
        """
        Provides the JSON representation of this object's state.

        @return: JSON representation of this object's state
        @rtype: string
        """
        return json.dumps(self._json_data, indent = indent)

    def print_json(self, indent = 4):
        """
        Prints JSON representation of this object's state.
        """
        print(self.get_real_json())

    def dump_json(self, output_file, indent = 4):
        """
        Writes JSON representation of this object's state to given file.

        @param output_file: path to output file
        @type output_file: String
        @param indent: Number of spaces per indent
        @type indent: Integer
        """
        with open(output_file, 'w') as f:
            json.dump(self._json_data, f, indent = indent)

    def load_json(self, input_file):
        """
        Sets this object's state using JSON representation in given file.

        @param input_file: Path to input file.
        @type input_file: String
        """
        with open(os.path.join(input_file), 'r') as f:
            self._json_data = self._load_from_file_and_keep_key_order(f)

    def _load_from_file_and_keep_key_order(self, f):
        return json.load(f, object_pairs_hook=OrderedDict)
