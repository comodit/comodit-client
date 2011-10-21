import json, os

class StringFactory(object):
    def new_object(self, json_data):
        return json_data

class JsonWrapper(object):
    def __init__(self, json_data = None):
        if(json_data):
            self.__json_data = json_data
        else:
            self.__json_data = {}

    def _get_field(self, field):
        return self.__json_data.get(field, None)

    def _set_field(self, field, value):
        self.__json_data[field] = value

    def _get_list_field(self, field, factory):
        object_list = []
        if(self.__json_data.has_key(field)):
            json_list = self.__json_data[field]
            for j in json_list:
                object_list.append(factory.new_object(j))
        return object_list

    def _add_to_list_field(self, field, value):
        if(not self.__json_data.has_key(field)):
            self.__json_data[field] = []
        if(isinstance(value, basestring)):
            self.__json_data[field].append(value)
        else:
            self.__json_data[field].append(value.get_json())

    def _set_list_field(self, field, object_list):
        json_list = []
        for o in object_list:
            json_list.append(o.get_json())
        self.__json_data[field] = json_list

    def set_json(self, json_data):
        self.__json_data = json_data

    def get_json(self):
        return self.__json_data
    
    def print_json(self):
        print json.dumps(self.__json_data)

    def dump_json(self, output_file, sort_keys=True, indent=4):
        with open(output_file, 'w') as f:
            json.dump(self.__json_data, f, sort_keys=sort_keys, indent=indent)

    def load_json(self, input_file):
        with open(os.path.join(input_file), 'r') as f:
            self.__json_data = json.load(f)
