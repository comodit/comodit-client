import unittest

import comodit_client.console.items as items

from comodit_client.console.paths import resolve_dots, absolute_elems, PathModel
from unittest import TestCase


class Mock:
    pass


class PathResolving(TestCase):

    def test_resolve_dots(self):
        self.assertEqual(resolve_dots(['x', '.']), ['x'])
        self.assertEqual(resolve_dots(['x', '.', 'y']), ['x', 'y'])
        self.assertEqual(resolve_dots(['x', 'y', '..']), ['x'])
        self.assertEqual(resolve_dots(['x', '..']), [])
        self.assertEqual(resolve_dots(['x', '..', 'y']), ['y'])
        self.assertEqual(resolve_dots(['x', 'y', 'z', '..', '..']), ['x'])
        self.assertEqual(resolve_dots(['..', '..']), [])

    def test_absolute_elems(self):
        current = Mock()
        current.absolute_path = 'x'
        self.assertEqual(absolute_elems(current, 'y'), ['x', 'y'])

    def test_absolute_elems_slash(self):
        current = Mock()
        self.assertEqual(absolute_elems(current, '/'), [])

    def test_resolve_root(self):
        (res_vars, node_type) = PathModel().resolve([])
        self.assertEqual(node_type['label'], items.RootItem)
        self.assertEqual(res_vars, {})

    def test_resolve_org(self):
        (res_vars, node_type) = PathModel().resolve(['organizations', 'name'])
        self.assertEqual(node_type['label'], items.OrganizationItem)
        self.assertEqual(res_vars, {'org_name': 'name'})

    def test_resolve_org_settings(self):
        (res_vars, node_type) = PathModel().resolve(['organizations', 'name', 'settings'])
        self.assertEqual(node_type['label'], items.OrgSettingsItem)
        self.assertEqual(res_vars, {'org_name': 'name'})

    def test_resolve_org_setting(self):
        (res_vars, node_type) = PathModel().resolve(['organizations', 'name1', 'settings', 'name2'])
        self.assertEqual(node_type['label'], items.OrgSettingItem)
        self.assertEqual(res_vars, {'org_name': 'name1', 'key': 'name2'})

    def test_resolve_envs(self):
        (res_vars, node_type) = PathModel().resolve(['organizations', 'name', 'environments'])
        self.assertEqual(node_type['label'], items.EnvironmentsItem)
        self.assertEqual(res_vars, {'org_name': 'name'})

    def test_resolve_env(self):
        (res_vars, node_type) = PathModel().resolve(['organizations', 'name1', 'environments', 'name2'])
        self.assertEqual(node_type['label'], items.EnvironmentItem)
        self.assertEqual(res_vars, {'org_name': 'name1', 'env_name': 'name2'})

    def test_resolve_env_settings(self):
        (res_vars, node_type) = PathModel().resolve(['organizations', 'name1', 'environments', 'name2', 'settings'])
        self.assertEqual(node_type['label'], items.EnvSettingsItem)
        self.assertEqual(res_vars, {'org_name': 'name1', 'env_name': 'name2'})

    def test_resolve_env_setting(self):
        (res_vars, node_type) = PathModel().resolve(['organizations', 'name1', 'environments', 'name2', 'settings', 'name3'])
        self.assertEqual(node_type['label'], items.EnvSettingItem)
        self.assertEqual(res_vars, {'org_name': 'name1', 'env_name': 'name2', 'key': 'name3'})

    def test_resolve_hosts(self):
        (res_vars, node_type) = PathModel().resolve(['organizations', 'name1', 'environments', 'name2', 'hosts'])
        self.assertEqual(node_type['label'], items.HostsItem)
        self.assertEqual(res_vars, {'org_name': 'name1', 'env_name': 'name2'})

    def test_resolve_host(self):
        (res_vars, node_type) = PathModel().resolve(['organizations', 'name1', 'environments', 'name2', 'hosts', 'name3'])
        self.assertEqual(node_type['label'], items.HostItem)
        self.assertEqual(res_vars, {'org_name': 'name1', 'env_name': 'name2', 'host_name': 'name3'})

    def test_resolve_host_settings(self):
        (res_vars, node_type) = PathModel().resolve(['organizations', 'name1', 'environments', 'name2', 'hosts', 'name3', 'settings'])
        self.assertEqual(node_type['label'], items.HostSettingsItem)
        self.assertEqual(res_vars, {'org_name': 'name1', 'env_name': 'name2', 'host_name': 'name3'})

    def test_resolve_host_setting(self):
        (res_vars, node_type) = PathModel().resolve(['organizations', 'name1', 'environments', 'name2', 'hosts', 'name3', 'settings', 'name4'])
        self.assertEqual(node_type['label'], items.HostSettingItem)
        self.assertEqual(res_vars, {'org_name': 'name1', 'env_name': 'name2', 'host_name': 'name3', 'key': 'name4'})

    def test_resolve_apps(self):
        (res_vars, node_type) = PathModel().resolve(['organizations', 'name', 'applications'])
        self.assertEqual(node_type['label'], items.ApplicationsItem)
        self.assertEqual(res_vars, {'org_name': 'name'})

    def test_resolve_app(self):
        (res_vars, node_type) = PathModel().resolve(['organizations', 'name1', 'applications', 'name2'])
        self.assertEqual(node_type['label'], items.ApplicationItem)
        self.assertEqual(res_vars, {'org_name': 'name1', 'app_name': 'name2'})

    def test_resolve_dists(self):
        (res_vars, node_type) = PathModel().resolve(['organizations', 'name', 'distributions'])
        self.assertEqual(node_type['label'], items.DistributionsItem)
        self.assertEqual(res_vars, {'org_name': 'name'})

    def test_resolve_dist(self):
        (res_vars, node_type) = PathModel().resolve(['organizations', 'name1', 'distributions', 'name2'])
        self.assertEqual(node_type['label'], items.DistributionItem)
        self.assertEqual(res_vars, {'org_name': 'name1', 'dist_name': 'name2'})

    def test_resolve_dist_settings(self):
        (res_vars, node_type) = PathModel().resolve(['organizations', 'name1', 'distributions', 'name2', 'settings'])
        self.assertEqual(node_type['label'], items.DistSettingsItem)
        self.assertEqual(res_vars, {'org_name': 'name1', 'dist_name': 'name2'})

    def test_resolve_dist_setting(self):
        (res_vars, node_type) = PathModel().resolve(['organizations', 'name1', 'distributions', 'name2', 'settings', 'name3'])
        self.assertEqual(node_type['label'], items.DistSettingItem)
        self.assertEqual(res_vars, {'org_name': 'name1', 'dist_name': 'name2', 'key': 'name3'})

    def test_resolve_plats(self):
        (res_vars, node_type) = PathModel().resolve(['organizations', 'name', 'platforms'])
        self.assertEqual(node_type['label'], items.PlatformsItem)
        self.assertEqual(res_vars, {'org_name': 'name'})

    def test_resolve_plat(self):
        (res_vars, node_type) = PathModel().resolve(['organizations', 'name1', 'platforms', 'name2'])
        self.assertEqual(node_type['label'], items.PlatformItem)
        self.assertEqual(res_vars, {'org_name': 'name1', 'plat_name': 'name2'})

    def test_resolve_plat_settings(self):
        (res_vars, node_type) = PathModel().resolve(['organizations', 'name1', 'platforms', 'name2', 'settings'])
        self.assertEqual(node_type['label'], items.PlatSettingsItem)
        self.assertEqual(res_vars, {'org_name': 'name1', 'plat_name': 'name2'})

    def test_resolve_plat_setting(self):
        (res_vars, node_type) = PathModel().resolve(['organizations', 'name1', 'platforms', 'name2', 'settings', 'name3'])
        self.assertEqual(node_type['label'], items.PlatSettingItem)
        self.assertEqual(res_vars, {'org_name': 'name1', 'plat_name': 'name2', 'key': 'name3'})

    def test_resolve_host_apps(self):
        (res_vars, node_type) = PathModel().resolve(['organizations', 'name1', 'environments', 'name2', 'hosts', 'name3', 'applications'])
        self.assertEqual(node_type['label'], items.HostAppsItem)
        self.assertEqual(res_vars, {'org_name': 'name1', 'env_name': 'name2', 'host_name': 'name3'})

    def test_resolve_host_app(self):
        (res_vars, node_type) = PathModel().resolve(['organizations', 'name1', 'environments', 'name2', 'hosts', 'name3', 'applications', 'name4'])
        self.assertEqual(node_type['label'], items.HostAppItem)
        self.assertEqual(res_vars, {'org_name': 'name1', 'env_name': 'name2', 'host_name': 'name3', 'app_name': 'name4'})

    def test_resolve_host_dist(self):
        (res_vars, node_type) = PathModel().resolve(['organizations', 'name1', 'environments', 'name2', 'hosts', 'name3', 'distribution'])
        self.assertEqual(node_type['label'], items.HostDistItem)
        self.assertEqual(res_vars, {'org_name': 'name1', 'env_name': 'name2', 'host_name': 'name3'})

    def test_resolve_host_plat(self):
        (res_vars, node_type) = PathModel().resolve(['organizations', 'name1', 'environments', 'name2', 'hosts', 'name3', 'platform'])
        self.assertEqual(node_type['label'], items.HostPlatItem)
        self.assertEqual(res_vars, {'org_name': 'name1', 'env_name': 'name2', 'host_name': 'name3'})

    def test_resolve_host_app_settings(self):
        (res_vars, node_type) = PathModel().resolve(['organizations', 'name1', 'environments', 'name2', 'hosts', 'name3', 'applications', 'name4', 'settings'])
        self.assertEqual(node_type['label'], items.HostAppSettingsItem)
        self.assertEqual(res_vars, {'org_name': 'name1', 'env_name': 'name2', 'host_name': 'name3', 'app_name': 'name4'})

    def test_resolve_host_app_setting(self):
        (res_vars, node_type) = PathModel().resolve(['organizations', 'name1', 'environments', 'name2', 'hosts', 'name3', 'applications', 'name4', 'settings', 'name5'])
        self.assertEqual(node_type['label'], items.HostAppSettingItem)
        self.assertEqual(res_vars, {'org_name': 'name1', 'env_name': 'name2', 'host_name': 'name3', 'app_name': 'name4', 'key': 'name5'})

    def test_resolve_host_dist_settings(self):
        (res_vars, node_type) = PathModel().resolve(['organizations', 'name1', 'environments', 'name2', 'hosts', 'name3', 'distribution', 'settings'])
        self.assertEqual(node_type['label'], items.HostDistSettingsItem)
        self.assertEqual(res_vars, {'org_name': 'name1', 'env_name': 'name2', 'host_name': 'name3'})

    def test_resolve_host_dist_setting(self):
        (res_vars, node_type) = PathModel().resolve(['organizations', 'name1', 'environments', 'name2', 'hosts', 'name3', 'distribution', 'settings', 'name4'])
        self.assertEqual(node_type['label'], items.HostDistSettingItem)
        self.assertEqual(res_vars, {'org_name': 'name1', 'env_name': 'name2', 'host_name': 'name3', 'key': 'name4'})

    def test_resolve_host_plat_settings(self):
        (res_vars, node_type) = PathModel().resolve(['organizations', 'name1', 'environments', 'name2', 'hosts', 'name3', 'platform', 'settings'])
        self.assertEqual(node_type['label'], items.HostPlatSettingsItem)
        self.assertEqual(res_vars, {'org_name': 'name1', 'env_name': 'name2', 'host_name': 'name3'})

    def test_resolve_host_plat_setting(self):
        (res_vars, node_type) = PathModel().resolve(['organizations', 'name1', 'environments', 'name2', 'hosts', 'name3', 'platform', 'settings', 'name4'])
        self.assertEqual(node_type['label'], items.HostPlatSettingItem)
        self.assertEqual(res_vars, {'org_name': 'name1', 'env_name': 'name2', 'host_name': 'name3', 'key': 'name4'})

    def test_resolve_host_instance(self):
        (res_vars, node_type) = PathModel().resolve(['organizations', 'name1', 'environments', 'name2', 'hosts', 'name3', 'instance'])
        self.assertEqual(node_type['label'], items.HostInstanceItem)
        self.assertEqual(res_vars, {'org_name': 'name1', 'env_name': 'name2', 'host_name': 'name3'})


if __name__ == '__main__':
    unittest.main()
