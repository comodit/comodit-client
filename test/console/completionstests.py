# coding: utf-8

import unittest

from comodit_client.console.completions import Completer
from comodit_client.console.items import Item

from unittest import TestCase


class Mock:
    pass


class ItemMock(Item):
    def __init__(self, conts, leaves):
        super(Item, self).__init__()
        self._conts = conts
        self._leaves = leaves

    @property
    def children_conts(self):
        return self._conts

    @property
    def children_leaves(self):
        return self._leaves


class MockNextItem:
    def __init__(self, conts, leaves):
        self._conts = conts
        self._leaves = leaves
        self._called = False

    def __call__(self, item_path):
        if self._called:
            raise Exception("Should not be called several times")

        self._called = True
        return ItemMock(self._conts, self._leaves)

def get_commands():
    return ['ls', 'cd']

def get_options(cmd):
    return ['-l', '--long']

def has_value(cmd, opt):
    return opt != '-l'

def mock_commands():
    cmds = Mock()
    cmds.get_commands = get_commands
    cmds.get_options = get_options
    cmds.has_value = has_value
    return cmds

class Changes(TestCase):

    def test_strip_tokens(self):
        cmds = mock_commands()
        completer = Completer(cmds, None)
        self.assertEqual(completer._strip_options(['cd', 'x']), ['cd', 'x'])
        self.assertEqual(completer._strip_options(['cd', '-l']), ['cd'])
        self.assertEqual(completer._strip_options(['cd', '--long', 'x']), ['cd'])

    def test_cmd_completion(self):
        line = ''
        cmds = mock_commands()

        current = ItemMock([], [])
        completer = Completer(cmds, current)
        self.assertEqual(completer.complete(line, '', 0), 'cd')
        self.assertEqual(completer.complete(line, '', 1), 'ls')
        self.assertEqual(completer.complete(line, '', 2), None)

    def test_empty_path_completion(self):
        line = 'ls '
        cmds = mock_commands()
        conts = ['container']
        leaves = ['leaf']

        current = ItemMock(conts, leaves)
        completer = Completer(cmds, current)
        completer._next_item = MockNextItem(conts, leaves)
        self.assertEqual(completer.complete(line, '', 0), 'container/')
        self.assertEqual(completer.complete(line, '', 1), 'leaf')
        self.assertEqual(completer.complete(line, '', 2), None)

    def test_option_completion(self):
        line = 'ls '
        cmds = mock_commands()
        conts = ['container']
        leaves = ['leaf']

        current = ItemMock(conts, leaves)
        completer = Completer(cmds, current)
        completer._next_item = MockNextItem(conts, leaves)
        self.assertEqual(completer.complete(line, '-', 0), '--long')
        self.assertEqual(completer.complete(line, '-', 1), '-l')
        self.assertEqual(completer.complete(line, '-', 2), None)

    def test_path_completion(self):
        line = 'ls '
        cmds = mock_commands()
        conts = ['container']
        leaves = ['leaf']

        current = ItemMock(conts, leaves)
        completer = Completer(cmds, current)
        completer._next_item = MockNextItem(conts, leaves)
        self.assertEqual(completer.complete(line, 'cont', 0), 'container/')
        self.assertEqual(completer.complete(line, 'cont', 1), None)

    def test_cont_with_spaces_completion(self):
        line = 'ls '
        cmds = mock_commands()
        conts = ['cont ainer']
        leaves = ['leaf']

        current = ItemMock(conts, leaves)
        completer = Completer(cmds, current)
        completer._next_item = MockNextItem(conts, leaves)
        self.assertEqual(completer.complete(line, 'cont', 0), 'cont\\ ainer/')
        self.assertEqual(completer.complete(line, 'cont', 1), None)

    def test_leaf_with_spaces_completion(self):
        line = 'ls '
        cmds = mock_commands()
        conts = ['container']
        leaves = ['le af']

        current = ItemMock(conts, leaves)
        completer = Completer(cmds, current)
        completer._next_item = MockNextItem(conts, leaves)
        self.assertEqual(completer.complete(line, 'le', 0), 'le\\ af')
        self.assertEqual(completer.complete(line, 'le', 1), None)

    def test_multi_path_completion(self):
        line = 'ls a/b/c'
        cmds = mock_commands()
        conts = ['container']
        leaves = ['leaf']

        current = ItemMock(conts, leaves)
        completer = Completer(cmds, current)
        completer._next_item = MockNextItem(conts, leaves)
        self.assertEqual(completer.complete(line, 'co', 0), 'container/')
        self.assertEqual(completer.complete(line, 'co', 1), None)


if __name__ == '__main__':
    unittest.main()
