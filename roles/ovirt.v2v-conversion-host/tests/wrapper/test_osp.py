import unittest
import virt_v2v_wrapper as wrapper


class TestOSP(unittest.TestCase):
    """ Tests specific to OpenStack """

    def test_disk_naming(self):
        host = wrapper.OSPHost()
        with self.assertRaises(ValueError):
            host._get_disk_name(0)
        self.assertEqual('vda', host._get_disk_name(1))
        self.assertEqual('vdb', host._get_disk_name(2))
        self.assertEqual('vdz', host._get_disk_name(26))
        self.assertEqual('vdaa', host._get_disk_name(27))
        self.assertEqual('vdab', host._get_disk_name(28))
        self.assertEqual('vdaz', host._get_disk_name(52))
        self.assertEqual('vdba', host._get_disk_name(53))
        self.assertEqual('vdzy', host._get_disk_name(701))
        self.assertEqual('vdzz', host._get_disk_name(702))
