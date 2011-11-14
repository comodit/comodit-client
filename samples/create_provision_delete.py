#
# Creates resources, provisions a host and then deletes resources using
# cortex-client API.
#

import create, delete, provision

if __name__ == "__main__":
    create.create_resources()
    provision.provision_host()
    delete.delete_resources()
