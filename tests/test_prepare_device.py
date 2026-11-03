import subprocess
import unittest
from unittest.mock import patch
from prepare_device import prepare_device

MOUNTED = [{'IsMounted': True, 'MountPath': '/System/Developer'}]


class PrepareTests(unittest.TestCase):
    @patch('prepare_device.subprocess.run')
    @patch('prepare_device.list_images', return_value=MOUNTED)
    def test_mounted_skips_download(self, images, run):
        prepare_device()
        run.assert_not_called()

    @patch('prepare_device.subprocess.run')
    @patch('prepare_device.list_images', side_effect=[[], MOUNTED])
    def test_mount_when_missing(self, images, run):
        prepare_device()
        run.assert_called_once()

    @patch('prepare_device.subprocess.run')
    @patch('prepare_device.list_images', side_effect=[[], []])
    def test_false_success_rejected(self, images, run):
        with self.assertRaises(RuntimeError):
            prepare_device()

    @patch('prepare_device.subprocess.run')
    @patch('prepare_device.list_images', side_effect=subprocess.CalledProcessError(1, 'list'))
    def test_list_error_does_not_download(self, images, run):
        with self.assertRaises(subprocess.CalledProcessError):
            prepare_device()
        run.assert_not_called()
