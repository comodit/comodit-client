import unittest

import comodit_client.console.utils as utils

from unittest import TestCase


class Mock:
    pass


class UtilsTesting(TestCase):

    def test_merge_escaped(self):
        result = utils.merge_escaped(["a", "test\\", "1\\", "2"])
        self.assertEqual(result, ["a", "test 1 2"])


if __name__ == '__main__':
    unittest.main()
