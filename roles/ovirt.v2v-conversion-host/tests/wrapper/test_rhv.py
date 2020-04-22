import unittest
try:
    # Python3
    from unittest.mock import patch
except ImportError:
    # Python2
    from mock import patch

import virt_v2v_wrapper as wrapper


class TestRHV(unittest.TestCase):
    """ Test specific to RHV """

    @patch('os.path.isfile', new=lambda _: True)
    def test_tools_iso_ordering(self):
        host = wrapper.VDSMHost()
        self.assertEqual(
                b'virtio-win-123.iso',
                host._filter_iso_names(b'/', [
                    b'a.iso',
                    b'virtio-win-123.iso',
                    b'b.iso',
                    ]))
        # Priority
        self.assertEqual(
                b'RHEV-toolsSetup_123.iso',
                host._filter_iso_names(b'/', [
                    b'RHEV-toolsSetup_123.iso',
                    b'virtio-win-123.iso',
                    ]))
        self.assertEqual(
                b'RHEV-toolsSetup_123.iso',
                host._filter_iso_names(b'/', [
                    b'virtio-win-123.iso',
                    b'RHEV-toolsSetup_123.iso',
                    ]))
        self.assertEqual(
                b'RHEV-toolsSetup_234.iso',
                host._filter_iso_names(b'/', [
                    b'RHEV-toolsSetup_123.iso',
                    b'virtio-win-123.iso',
                    b'RHEV-toolsSetup_234.iso',
                    ]))
        self.assertEqual(
                b'RHEV-toolsSetup_234.iso',
                host._filter_iso_names(b'/', [
                    b'RHEV-toolsSetup_234.iso',
                    b'virtio-win-123.iso',
                    b'RHEV-toolsSetup_123.iso',
                    ]))
        self.assertEqual(
                b'rhv-tools-setup.iso',
                host._filter_iso_names(b'/', [
                    b'rhv-tools-setup.iso',
                    b'virtio-win-123.iso',
                    ]))
        # Version
        self.assertEqual(
                b'RHEV-toolsSetup_4.0_3.iso',
                host._filter_iso_names(b'/', [
                    b'RHEV-toolsSetup_4.0_3.iso',
                    b'RHEV-toolsSetup_4.0_2.iso',
                    ]))

        self.assertEqual(
                b'RHEV-toolsSetup_4.1_3.iso',
                host._filter_iso_names(b'/', [
                    b'RHEV-toolsSetup_4.0_3.iso',
                    b'RHEV-toolsSetup_4.1_3.iso',
                    ]))

    VDDK_RHV = {
        'vm_name': 'My Virtual',
        'transport_method': 'vddk',

        'rhv_url': 'https://example.my-ovirt.org/ovirt-engine/api',
        'rhv_password_file': '/rhv/password',
        'rhv_cluster': 'Default',
        'rhv_storage': 'data',
        'rhv_cafile': '/rhv/ca.pem',

        'vmware_fingerprint': '01:23:45:67:89:AB:CD:EA:DB:EE:F0:12:34:56:78:9A:BC:DE:F0:12',  # NOQA E501
        'vmware_uri': 'esx://root@1.2.3.4?',
        'vmware_password_file': '/vmware/password',

        'install_drivers': False,
        'output_format': 'raw',
        'insecure_connection': False,
    }

    VDDK_EXPORT = {
        'vm_name': 'My Virtual',
        'transport_method': 'vddk',

        'export_domain': '1.2.3.4:/export/domain',

        'vmware_fingerprint': '01:23:45:67:89:AB:CD:EA:DB:EE:F0:12:34:56:78:9A:BC:DE:F0:12',  # NOQA E501
        'vmware_uri': 'esx://root@1.2.3.4?',
        'vmware_password_file': '/vmware/password',

        'install_drivers': False,
        'output_format': 'raw',
        'insecure_connection': False,
    }

    def test_vddk_rhv_basic(self):
        data = self.VDDK_RHV.copy()
        expected = [
            '-of', 'raw',
            '-o', 'rhv-upload',
            '-oc', 'https://example.my-ovirt.org/ovirt-engine/api',
            '-os', 'data',
            '-op', '/rhv/password',
            '-oo', 'rhv-cafile=/rhv/ca.pem',
            '-oo', 'rhv-cluster=Default',
            '-oo', 'rhv-direct',
        ]
        host = wrapper.BaseHost.factory(wrapper.BaseHost.TYPE_VDSM)
        v2v_args, v2v_env = host.prepare_command(
                data, [], {}, [])
        self.assertEqual(v2v_args, expected)

    def test_vddk_rhv_insecure(self):
        data = self.VDDK_RHV.copy()
        data['insecure_connection'] = True
        expected = [
            '-of', 'raw',
            '-o', 'rhv-upload',
            '-oc', 'https://example.my-ovirt.org/ovirt-engine/api',
            '-os', 'data',
            '-op', '/rhv/password',
            '-oo', 'rhv-cafile=/rhv/ca.pem',
            '-oo', 'rhv-cluster=Default',
            '-oo', 'rhv-direct',
            '-oo', 'rhv-verifypeer=false',
        ]
        host = wrapper.BaseHost.factory(wrapper.BaseHost.TYPE_VDSM)
        v2v_args, v2v_env = host.prepare_command(
                data, [], {}, [])
        self.assertEqual(v2v_args, expected)

    def test_vddk_export(self):
        data = self.VDDK_EXPORT.copy()
        expected = [
            '-of', 'raw',
            '-o', 'rhv',
            '-os', '1.2.3.4:/export/domain',
        ]
        host = wrapper.BaseHost.factory(wrapper.BaseHost.TYPE_VDSM)
        v2v_args, v2v_env = host.prepare_command(
                data, [], {}, [])
        self.assertEqual(v2v_args, expected)
