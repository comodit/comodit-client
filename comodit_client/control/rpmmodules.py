from comodit_client.control import completions
from comodit_client.control.entity import EntityController
from comodit_client.control.exceptions import ArgumentException


class RpmModuleController(EntityController):

    _template = "rpmmodules.json"

    def __init__(self):
        super(RpmModuleController, self).__init__()

    def get_collection(self, argv):
        return self._client.rpm_modules(argv[0], argv[1])

    def _print_collection_completions(self, param_num, argv):
        if param_num == 0:
            completions.print_identifiers(self._client.organizations())
        elif len(argv) > 0 and param_num == 1:
            completions.print_identifiers(self._client.applications(argv[0]))
        elif len(argv) > 0 and param_num == 2:
            completions.print_identifiers(self._client.rpm_modules(argv[0], argv[1]))

    def _get_name_argument(self, argv):
        if len(argv) < 3:
            raise ArgumentException("Wrong number of arguments");

        return argv[2]

    def _print_entity_completions(self, param_num, argv):
        self._print_collection_completions(param_num, argv)