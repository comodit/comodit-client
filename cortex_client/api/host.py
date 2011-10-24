from cortex_client.api.resource import Resource
from cortex_client.rest.exceptions import ApiException
from cortex_client.util.json_wrapper import JsonWrapper, StringFactory
from exceptions import PythonApiException

class Setting(JsonWrapper):
    def __init__(self, json_data = None):
        super(Setting, self).__init__(json_data)

    def get_value(self):
        return self._get_field("value")

    def get_key(self):
        return self._get_field("key")

    def get_version(self):
        return self._get_field("version")

    def show(self, indent = 0):
        print " "*indent, "Key:", self.get_key()
        print " "*indent, "Value:", self.get_value()
        print " "*indent, "Version:", self.get_version()


class SettingFactory(object):
    def new_object(self, json_data):
        return Setting(json_data)


class HostInfo(JsonWrapper):
    def __init__(self, json_data = None):
        super(HostInfo, self).__init__(json_data)

    def get_state(self):
        return self._get_field("state")

    def show(self, indent = 0):
        print " "*indent, self.get_state()

class Host(Resource):
    def __init__(self, api = None, json_data = None):
        super(Host, self).__init__(json_data)
        if(api):
            self.set_api(api)

    def set_api(self, api):
        super(Host, self).set_api(api)
        self._set_collection(api.get_host_collection())

    def get_organization(self):
        return self._get_field("organization")

    def set_organization(self, organization):
        self._set_field("organization", organization)

    def get_environment(self):
        return self._get_field("environment")

    def set_environment(self, environment):
        self._set_field("environment", environment)

    def get_platform(self):
        return self._get_field("platform")

    def set_platform(self, platform):
        self._set_field("platform", platform)

    def get_distribution(self):
        return self._get_field("distribution")

    def set_distribution(self, distribution):
        self._set_field("distribution", distribution)

    def get_settings(self):
        return self._get_list_field("settings", SettingFactory())

    def set_settings(self, settings):
        self._set_list_field("settings", settings)

    def add_setting(self, setting):
        self._add_to_list_field("settings", setting)

    def get_applications(self):
        return self._get_list_field("applications", StringFactory())

    def set_applications(self, applications):
        self._set_list_field("applications", applications)
        
    def add_application(self, application):
        self._add_to_list_field("applications", application)

    def get_version(self):
        self._get_field("version")

    def delete(self, delete_vm = False):
        if(delete_vm):
            try:
                self._api.get_client().update("hosts/" + self.get_uuid() + "/_delete",
                                              decode=False)
            except ApiException, e:
                if(e.code == 400):
                    print "Could not delete VM:", e.message
                else:
                    raise e
        self._api.get_client().delete("hosts/" + self.get_uuid())

    def get_state(self):
        result = self._api.get_client().read("hosts/" + self.get_uuid()+"/state")
        return HostInfo(result)

    def get_identifier(self):
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
        print " "*indent, "Settings:"
        settings = self.get_settings()
        for s in settings:
            s.show(indent=(indent + 2))
            print

    def provision(self):
        uuid = self.get_uuid()
        client = self._api.get_client()
        try:
            client.update("provisioner/_provision",
                      parameters={"hostId":uuid}, decode=False)
        except ApiException, e:
            raise PythonApiException("Unable to provision host", e)

    def start(self):
        result = self._api.get_client().update("hosts/"+self.get_uuid()+"/_start", decode=False)
        if(result.getcode() != 202):
            raise PythonApiException("Call not accepted by server")

    def pause(self):
        result = self._api.get_client().update("hosts/"+self.get_uuid()+"/_pause", decode=False)
        if(result.getcode() != 202):
            raise PythonApiException("Call not accepted by server")

    def resume(self):
        result = self._api.get_client().update("hosts/"+self.get_uuid()+"/_resume", decode=False)
        if(result.getcode() != 202):
            raise PythonApiException("Call not accepted by server")

    def shutdown(self):
        result = self._api.get_client().update("hosts/"+self.get_uuid()+"/_stop", decode=False)
        if(result.getcode() != 202):
            raise PythonApiException("Call not accepted by server")

    def poweroff(self):
        try:
            result = self._api.get_client().update("hosts/"+self.get_uuid()+"/_off", decode=False)
            if(result.getcode() != 202):
                raise PythonApiException("Call not accepted by server")
        except ApiException, e:
            raise PythonApiException("Unable to poweroff host", e)
