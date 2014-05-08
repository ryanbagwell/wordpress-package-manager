import unittest
import subprocess
import shutil
import os


class WordpressPMTests(unittest.TestCase):
    wpm_path = os.path.join(os.path.dirname(__file__), '../wpm')
    test_dir = os.path.join(os.path.dirname(__file__), '..', '_test')

    def setUp(self):

        try:
            shutil.rmtree(self.test_dir)
        except:
            pass

        os.makedirs(os.path.join(self.test_dir))

    def tearDown(self):

        try:
            shutil.rmtree(self.test_dir)
        except:
            pass

    def test_install_framework(self):
        """ Download and upack the latest wordpress framework """
        subprocess.call("%s installframework %s/public" %
                        (self.wpm_path, self.test_dir), shell=True)

        """ Check that it's in the correct location """
        self.assertTrue(os.path.exists(
            os.path.join(self.test_dir, 'public', 'wp-config.php')),
            msg="wp-config.php not found.")


if __name__ == '__main__':
    unittest.main()
