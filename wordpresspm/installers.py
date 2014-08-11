#! /usr/bin/env python
import os
import sys
import re
import zipfile
import shutil
import urllib2
import subprocess
import tempfile
import urllib


class BaseInstaller(object):
    wpm_meta_path = os.path.expanduser('~/.wpm/')
    plugin_db_path = os.path.join(wpm_meta_path, 'available_plugins')
    tmp_dir = tempfile.mkdtemp()
    plugins_svn = "http://plugins.svn.wordpress.org"
    target_location = None
    plugin_name = ''

    def __init__(self, *args, **kwargs):

        for key, value in kwargs.items():
            setattr(self, key, value)

    def download_file(self, url):
        """ Common method to download a file from a given url """

        print 'Fetching %s' % url

        temp = tempfile.mkstemp()

        urllib.urlretrieve(url, temp[1])

        return temp[1]

    def extract(self, file):
        """ Extract the contents of a zip file """

        print "Unzipping %s" % file

        z = zipfile.ZipFile(file)

        z.extractall(self.tmp_dir)

        return z.namelist()

    def set_security_keys(self, config_file=None):
        """ Generates new security keys and writes them
            to the wp-config.php file """

        if not config_file:
            return

        print "Generating new security keys"

        try:
            keys = urllib2.urlopen(
                'https://api.wordpress.org/secret-key/1.1/salt/').readlines()
        except:
            print "Couldn't generate security keys from WordPress API. You'll have to set them yourself."
            return

        config_file = open(self.target_location + '/wp-config.php', 'r+')

        lines = config_file.readlines()

        for i in range(len(lines)):
            for key in keys:
                match = re.findall("^define\('(.*)',", key)
                if match is not None and match[0] in lines[i]:
                    lines[i] = key

        config_file.seek(0)

        config_file.writelines(lines)

    def run_command(self, cmd_list):
        """ Runs a shell command command """

        proc = subprocess.Popen(cmd_list, stdout=subprocess.PIPE)

        for line in proc.stdout:
            if line is not "\r\n":
                print line

    def move_tmp(self, src, dest):
        """ Renames the tmp installation dir to the
            specified destination """

        if os.path.exists(os.path.abspath(dest)) and not self.overwrite:
            print "Installation already exists"
            return False

        try:
            shutil.rmtree(os.path.abspath(dest))
        except:
            pass

        shutil.move(src, dest)

    def install(self):

        if os.path.exists(os.path.join(self.target_location, self.plugin_name)) and not self.overwrite:
            print "Target location for %s exists. Aborting." % self.plugin_name
            return False

        return True


class ZIPInstaller(BaseInstaller):

    """ Downloads, unpacks and relocates
        a remote zip file """

    def install(self):
        _continue = super(ZIPInstaller, self).install()

        if _continue is False:
            return

        target_location = os.path.join(self.target_location, self.plugin_name)

        file = self.download_file(self.url)

        self.extract(file)

        self.move_tmp(self.tmp_dir, target_location)

        return True


class WPZIPInstaller(ZIPInstaller):

    """ Installs a plugin from the official wordpress plugins site. """

    def move_tmp(self, src, dest):
        """ A conventional Wordpress plugin will have only one directory whose
            name will be the same as the plugin's name. Here, we'll add that
            directory name to our path """

        src = os.path.join(src, self.plugin_name)

        super(WPZIPInstaller, self).move_tmp(src, dest)


class GITInstaller(BaseInstaller):

    """ Clones a git repository """

    def install(self):
        _continue = super(GITInstaller, self).install()

        if _continue is False:
            return

        print "Cloning %s from %s" % (self.plugin_name, self.url)

        self.run_command(
            ['git', 'clone', self.url, os.path.join(self.target_location, self.plugin_name)])


class SVNInstaller(BaseInstaller):

    """ Exports from the trunk of an svn repository """

    def install(self):
        _continue = super(SVNInstaller, self).install()

        if _continue is False:
            return

        print "Exporting %s from %s" % (self.plugin_name, self.svn_url)

        self._run_command(['svn', 'export', self.url, self.target_location])


class WPInstaller(BaseInstaller):

    """ Download and extract the specified plugin from the
        official WordPress SVN plugin repository """

    def install(self):
        super(WPInstaller, self).install()

        """ Build the url to the svn repo """
        svn_url = '/'.join([self.plugins_svn,
                            self.plugin_name.replace("\n", ''), 'trunk'])

        print "Exporting %s from Wordpress SVN" % (self.plugin_name)

        self.run_command(['svn', 'export', svn_url,
                          os.path.join(self.target_location, self.plugin_name)])


class FrameworkInstaller(ZIPInstaller):

    """ Downlads and installs the WP framework """

    def install(self):

        file = self.download_file(self.url)

        self.extract(file)

        self.move_tmp(
            os.path.join(self.tmp_dir, 'wordpress'), self.target_location)

        return True


class DBInstaller(BaseInstaller):

    """ Creates the wpm meta directory,
        and downlods the list of available plugins. """

    def install(self):

        data = self.download_file(self.plugins_svn)

        try:
            os.mkdir(self.wpm_meta_path)
        except OSError:
            print "WPM meta directory already exists (%s). Continuing"

        local = open(self.plugin_db_path, 'w+')

        list(local.read())

        plugins = re.findall('">(.*)/</a>', data)

        local.seek(0)
        local.write("\r\n".join(plugins))

        local.close()
