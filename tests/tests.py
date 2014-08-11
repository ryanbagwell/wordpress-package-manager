import unittest
import subprocess
import shutil
import os


class WordpressPMTests(unittest.TestCase):
    wpm_path = os.path.join(os.path.dirname(__file__), '../wordpresspm/wpm')
    test_dir = os.path.join(os.path.dirname(__file__), '..', '_test')

    @classmethod
    def setUpClass(self):

        try:
            shutil.rmtree(self.test_dir)
        except:
            pass

        os.makedirs(os.path.join(self.test_dir))

    @classmethod
    def tearDownClass(self):
        try:
            shutil.rmtree(self.test_dir)
        except:
            pass

    def test_install_framework(self):
        """ Download and upack the latest wordpress framework """
        subprocess.call("python %s installframework %s/public" %
                        (self.wpm_path, self.test_dir), shell=True)

        """ Check that it's in the correct location """
        self.assertTrue(os.path.exists(
            os.path.join(self.test_dir, 'public', 'wp-config.php')),
            msg="wp-config.php not found.")

    def test_install_plugin(self):

        subprocess.call(
            "python %s installplugin cloudflare==1.3.14 -l %s/public/wp-content/plugins/" %
            (self.wpm_path, self.test_dir), shell=True)

        self.assertTrue(os.path.exists(
            os.path.join(
                self.test_dir, 'public/wp-content/plugins/cloudflare/cloudflare.php')),
            msg="cloudflare.php not found.")

    def test_install_plugin_from_zip(self):

        cmd = ' '.join([
            'python',
            self.wpm_path,
            'installplugin',
            'zip+http://www3.formassembly.com/plugins/wordpress/wp_formassembly.zip#name=form-assembly',
            '-l',
            '%s/public/wp-content/plugins/' % self.test_dir,
        ])

        subprocess.call(cmd, shell=True)

        self.assertTrue(os.path.exists(
            os.path.join(
                self.test_dir, 'public/wp-content/plugins/form-assembly/wp_formassembly.php')),
            msg="wp_formassembly.php not found.")


    def test_install_plugin_from_git(self):

        cmd = ' '.join([
            'python',
            self.wpm_path,
            'installplugin',
            'git+git@github.com:ryanbagwell/wordpress-sentry.git#name=wordpress-sentry',
            '-l',
            '%s/public/wp-content/plugins/' % self.test_dir,
        ])

        subprocess.call(cmd, shell=True)

        self.assertTrue(os.path.exists(
            os.path.join(
                self.test_dir, 'public/wp-content/plugins/wordpress-sentry/wordpress-sentry.php')),
            msg="wordpress-sentry.php not found.")

    def test_install_plugins_from_requirements_file(self):

        shutil.rmtree(
            os.path.join(self.test_dir, 'public', 'wp-content', 'plugins'))

        cmd = ' '.join([
            'python',
            self.wpm_path,
            'installplugin',
            '-r',
            os.path.join(self.test_dir, '..', 'tests', 'requirements.wpm'),
            '-l',
            os.path.join(self.test_dir, 'public', 'wp-content', 'plugins'),
        ])

        subprocess.call(cmd, shell=True)

        self.assertTrue(os.path.exists(
            os.path.join(
                self.test_dir, 'public/wp-content/plugins/wordpress-sentry/wordpress-sentry.php')),
            msg="wordpress-sentry.php not found.")

        self.assertTrue(os.path.exists(
            os.path.join(
                self.test_dir, 'public/wp-content/plugins/form-assembly/wp_formassembly.php')),
            msg="wp_formassembly.php not found.")

        self.assertTrue(os.path.exists(
            os.path.join(
                self.test_dir, 'public/wp-content/plugins/w3-total-cache/w3-total-cache.php')),
            msg="w3-total-cache.php not found.")


if __name__ == '__main__':
    unittest.main()
