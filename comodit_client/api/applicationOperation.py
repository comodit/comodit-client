from comodit_client.util.json_wrapper import JsonWrapper


class ApplicationOperation(JsonWrapper):
    """
        ApplicationOperation of orchestration
    """

    @property
    def application(self):
        return self._get_field("application")

    @property
    def handler(self):
        return self._get_field("handler")

    @property
    def position(self):
        return self._get_field("position")

    @property
    def service_action(self):
        """
        serviceAction to apply

        @rtype: ServiceAction
        """

        return ServiceAction(self._get_field("serviceAction"))

    def _show(self, indent=0):
        print(" " * indent, "Position:", self.position)
        print(" " * indent, "Application:", self.application)
        print(" " * indent, "Handler:", self.handler)
        self.service_action._show(indent + 2)


class ServiceAction(JsonWrapper):
    @property
    def name(self):
        return self._get_field("name")

    @name.setter
    def name(self, name):
        """
        Set service name
        """

        self._set_field("name", name.get_json())

    @property
    def action(self):
        return self._get_field("action")

    @action.setter
    def action(self, action):
        """
        Set action service
        """

        self._set_field("action", action.get_json())

    def _show(self, indent=0):
        print(" " * indent, "Service name:", self.name)
        print(" " * indent, "Action:", self.action)
