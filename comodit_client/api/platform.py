# coding: utf-8
"""
Provides classes related to platform entity, in particular L{Platform}
and L{PlatformCollection}.
"""
from __future__ import print_function

from comodit_client.api.collection import Collection
from comodit_client.api.exceptions import PythonApiException
from comodit_client.api.files import HasFiles
from comodit_client.api.parameters import HasParameters, Parameter
from comodit_client.api.settings import HasSettings, _build_setting, Setting
from comodit_client.rest.exceptions import ApiException
from comodit_client.util.json_wrapper import JsonWrapper


class PlatformCollection(Collection):
    """
    Collection of platforms. A platform collection is owned by an
    L{Organization}.
    """

    def _new(self, json_data = None):
        return Platform(self, json_data)

    def new(self, name, description = "", driver_class = ""):
        """
        Instantiates a new platform object.

        @param name: The name of new platform.
        @type name: string
        @param description: The description of new platform.
        @type description: string
        @param driver_class: Class name of the platform's driver.
        @type driver_class: string
        @rtype: L{Platform}
        """

        plat = self._new()
        plat.name = name
        plat.driver = Driver()
        plat.driver.class_name = driver_class
        plat.description = description
        return plat

    def create(self, name, description = "", driver_class = "", default = True, test = True):
        """
        Creates a remote platform entity and returns associated local
        object.

        @param name: The name of new distribution.
        @type name: string
        @param description: The description of new distribution.
        @type description: string
        @param driver_class: Class name of the platform's driver.
        @type driver_class: string
        @rtype: L{Platform}
        """

        plat = self.new(name, description, driver_class)
        plat.create(parameters = {"default": "true" if default else "false", "test": "true" if test else "false"})
        return plat


class Driver(JsonWrapper):
    """
    Platform driver representation. A driver is uniquely defined by its
    Java class canonical name. Available drivers are:
      - com.guardis.cortex.server.driver.AmazonEc2Driver
      - com.guardis.cortex.server.driver.CloudStackDriver
      - com.guardis.cortex.server.driver.EucalyptusDriver
      - com.guardis.cortex.server.driver.FreeDriver
      - com.guardis.cortex.server.driver.OpenStackDriver
      - com.guardis.cortex.server.driver.PxeDriver
      - com.guardis.cortex.server.driver.RackspaceDriver
      - com.guardis.cortex.server.driver.RackspaceDriver2
      - com.guardis.cortex.server.driver.SynapseAgentDriver

    @see: L{Platform}
    """

    @property
    def name(self):
        """
        The name of the driver.

        @rtype: string
        """
        return self._get_field("name")

    @property
    def description(self):
        """
        The description of the driver.

        @rtype: string
        """

        return self._get_field("description")

    @property
    def class_name(self):
        """
        The Java class canonical name of the driver.

        @rtype: string
        """

        return self._get_field("className")

    @class_name.setter
    def class_name(self, name):
        """
        Sets Java class canonical name of the driver.

        @param name: The Java class canonical name of the driver.
        @type name: string
        """

        self._set_field("className", name)

    def show(self, indent = 0):
        """
        Prints driver's representation to standard output in a user-friendly way.

        @param indent: The number of spaces to put in front of each displayed
        line.
        @type indent: int
        """

        print(" "*indent, "Name:", self.name)
        print(" "*indent, "Description:", self.description)
        print(" "*indent, "Driver class:", self.class_name)


class Image(JsonWrapper):
    """
    Platform image representation. An image can be created from an L{Instance} with some driver types.
    The image can later be re-used to duplicate the instance.

    @see: L{Platform}
    @see: L{Instance}
    """

    @property
    def image_id(self):
        """
        Image's ID.

        @rtype: string
        """

        return self._get_field("id")

    @property
    def name(self):
        """
        Image's name.

        @rtype: string
        """

        return self._get_field("name")

    @property
    def create_distribution(self):
        """
        Image's "create distribution" flag (telling if a L{Distribution} was created alongside the image).

        @rtype: string
        """

        return self._get_field("createDistribution")

    @create_distribution.setter
    def create_distribution(self, create_distribution):
        """
        Sets "create distribution" flag.

        @param create_distribution: flag value
        """

        self._set_field("createDistribution", create_distribution)

    @property
    def settings(self):
        """
        Lists the settings of this image. Note that this list is only defined when creating
        an image. When reading the image later, settings are not available anymore.

        @rtype list of unconnected L{Setting}s
        """

        return self._get_list_field("settings", lambda x: Setting(None, x))

    @settings.setter
    def settings(self, settings):
        """
        Sets the list of settings required when creating an image. The settings must match the list
        of L{Parameter}s provided by the L{Platform}.

        @param settings: The list of settings provided when creating an image (see L{Instance})

        @see L{Platform}
        @see L{Instance}
        """

        self._set_list_field("settings", settings)

    def show(self, indent = 0):
        """
        Prints image's representation to standard output in a user-friendly way.

        @param indent: The number of spaces to put in front of each displayed
        line.
        @type indent: int
        """

        print(" "*indent, "ID:", self.image_id)
        print(" "*indent, "Name:", self.name)


class Platform(HasSettings, HasParameters, HasFiles):
    """
    Platform entity representation. A platform defines the
    way a particular host will be provisioned by configuring a driver.
    A platform may have files, parameters and settings.

    A platform entity owns 3 collections:
      - settings (L{Setting})
      - parameters (L{Parameter})
      - files (L{File})
    """

    @property
    def driver(self):
        """
        Platform's driver.

        @rtype: L{Driver}
        """

        return Driver(self._get_field("driver"))

    @driver.setter
    def driver(self, driver):
        """
        Sets platform's driver.

        @param driver: Platform's driver.
        @type driver: L{Driver}
        """

        self._set_field("driver", driver.get_json())

    def clone(self, clone_name):
        """
        Requests the cloning of remote entity. Clone will have given name.
        This name should not already be in use.

        @param clone_name: The name of the clone.
        @type clone_name: string
        @return: The representation of platform's clone.
        @rtype: L{Platform}
        """

        try:
            result = self._http_client.update(self.url + "_clone", parameters = {"name": clone_name})
            return Platform(self.collection, result)
        except ApiException as e:
            raise PythonApiException("Unable to clone platform: " + e.message)

    def _show(self, indent = 0):
        super(Platform, self)._show(indent)

        print(" "*indent, "Driver:")
        self.driver.show(indent + 2)

        self._show_settings(indent)
        self._show_parameters(indent)
        self._show_files(indent)

    def list_images(self):
        try:
            result = self._http_client.read(self.url + "images")
            return [ Image(item) for item in result['items']]
        except ApiException as e:
            raise PythonApiException("Unable to retrieve platform images: " + e.message)

    def image_parameters(self):
        try:
            result = self._http_client.read(self.url + "driver/image_parameters")
            return [ Parameter(None, item) for item in result['items']]
        except ApiException as e:
            raise PythonApiException("Unable to retrieve image parameters: " + e.message)
