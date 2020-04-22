import logging
import unittest
try:
    # Python 2
    from cStringIO import StringIO
except ImportError:
    # Python 3
    from io import StringIO

import virt_v2v_wrapper as wrapper


class TestRoutines(unittest.TestCase):
    """ Test basic routines """
    def setUp(self):
        self.maxDiff = None

    def test_log_command_safe(self):
        logging.basicConfig()
        test_log = logging.getLogger('test-safe')
        test_log.propagate = False
        test_log.setLevel(logging.DEBUG)
        for h in test_log.handlers:
            test_log.removeHandler(h)
        log_stream = StringIO()
        test_log.addHandler(logging.StreamHandler(log_stream))
        wrapper.log_command_safe([
                'virt-v2v',
                '--password-file', '/some/password/file',
                '-op', '/some/other/password/file',
                '-oo', 'os-some-password=secret',
                '-oo', 'os-some-other-password=password',
            ],
            {}, test_log)
        # Expected results
        expected_args = [
            'virt-v2v',
            '--password-file', '/some/password/file',
            '-op', '/some/other/password/file',
            '-oo', 'os-some-password=*****',
            '-oo', 'os-some-other-password=*****',
        ]
        expected_env = {}
        expected = 'Executing command: %r, environment: %r\n' % \
            (expected_args, expected_env)
        self.assertEqual(
            expected,
            log_stream.getvalue())

    # @unittest.skip("Broken test")
    def test_log_command_safe2(self):

        logging.basicConfig()
        test_log = logging.getLogger('test-safe')
        test_log.propagate = False
        test_log.setLevel(logging.DEBUG)
        for h in test_log.handlers:
            test_log.removeHandler(h)
        log_stream = StringIO()
        test_log.addHandler(logging.StreamHandler(log_stream))
        wrapper.log_command_safe(
            ['virt-v2v'],
            {
                'PATH': '/some/path',
                'OS_SOME_PASSWORD': 'secret',
                'OS_SOME_OTHER_PASSWORD': 'password',
            }, test_log)
        # Expected results
        expected_args = ['virt-v2v']
        # TODO: this does not work well, the order of items is not stable
        expected_env = {
            'PATH': '/some/path',
            'OS_SOME_PASSWORD': '*****',
            'OS_SOME_OTHER_PASSWORD': '*****',
        }
        expected = 'Executing command: %r, environment: %r\n' % \
            (expected_args, expected_env)
        self.assertEqual(
                expected,
                log_stream.getvalue())
