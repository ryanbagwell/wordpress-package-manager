#! /usr/bin/env python
import sys, os, re, zipfile, shutil, urllib2, urllib, subprocess, re, tempfile, urlparse
from progressbar import ProgressBar, Percentage, Bar, FormatLabel
import subprocess

class BaseInstaller(object):
    wpm_meta_path = os.path.expanduser('~/.wpm/')
    plugin_db_path = os.path.join(wpm_meta_path, 'available_plugins')
    tmp_dir = tempfile.mkdtemp()
    plugins_svn = "http://plugins.svn.wordpress.org"
    target_location = None

    def __init__(self, *args, **kwargs):

        for key, value in kwargs.items():
            setattr(self, key, value)

    """
    Common method to download a file from a given url
    """
    def download_file(self, url):
        return self.download_data(url)


    def download_data(self, url):

        pbar = ProgressBar(widgets=[FormatLabel('Downloading'), Percentage(), Bar()],
            maxval=9000000).start()

        temp = tempfile.mkstemp()

        p = subprocess.Popen(['wget', '-O', temp[1], url], stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

        while p.poll() != 0:
            pbar.update(os.stat(temp[1]).st_size)

        pbar.finish()

        return temp[1]


    """
    Unzip a plugin in .zip format
    """
    def extract(self, file):
        print "\r\nUnzipping ..."
        z = zipfile.ZipFile(file)
        z.extractall(self.tmp_dir)
        return z.namelist()

        #return os.path.join(self.tmp_dir, z.namelist())


    """
    Writes new security keys to the wp-config.php file
    """
    def set_security_keys(self, config_file = None):

        if not config_file:
            return

        print "Generating new security keys"

        try:
            keys = urllib2.urlopen('https://api.wordpress.org/secret-key/1.1/salt/').readlines()
        except:
            print "Couldn't generate security keys from WordPress API. You'll have to set them yourself."
            return;

        config_file = open(self.target_location+'/wp-config.php','r+')
        lines = config_file.readlines()

        for i in range(len(lines)):
            for key in keys:
                match = re.findall("^define\('(.*)',", key)
                if match is not None and match[0] in lines[i]:
                    lines[i] = key

        config_file.seek(0)
        config_file.writelines(lines)

    """
    Runs a command
    """
    def run_command(self, cmd_list):
        proc = subprocess.Popen(cmd_list,stdout=subprocess.PIPE)
        for line in proc.stdout:
            if line is not "\r\n": print line

    """
    Moves the tmp install to the specified plugin location
    """
    def move_tmp(self, src, dest):

        if os.path.exists(os.path.abspath(dest)) and not self.overwrite:
            print "Installation already exists"
            return False

        try:
            shutil.rmtree(os.path.abspath(dest))
        except:
            pass

        shutil.move(src, dest)


class ZIPInstaller(BaseInstaller):

    def __init__(self, *args, **kwargs):
        super(ZIPInstaller, self).__init__(*args, **kwargs)


    def install(self):

        target_location = os.path.join(self.target_location, self.plugin_name)

        file = self.download_file(self.url)

        extracted_files = self.extract(file)

        self.move_tmp(self.tmp_dir, target_location)

        return True

class GITInstaller(BaseInstaller):
    """
    Clones a git repository
    """
    def install(self):
        print "Cloning %s from %s" % (self.plugin_name, self.url)
        self.run_command(['git','clone', self.url, os.path.join(self.target_location, self.plugin_name) ])


"""
Exports from the trunk of an svn repository
"""
class SVNInstaller(BaseInstaller):

    def install(self):
        print "Exporting %s from %s" % (self.plugin_name, self.svn_url)
        self._run_command(['svn','export', url, self.target_location ])

"""
Download and extract the specified plugin from the
official WordPress plugin repository
"""
class WPInstaller(BaseInstaller):

    def install(self):

        if os.path.exists(
            os.path.join(self.target_location, self.plugin_name)) and not self.overwrite:
            print "Target location exists. Aborting"
            return

        svn_url = '/'.join([self.plugins_svn, self.plugin_name.replace("\n",''), 'trunk'])
        print "Exporting %s from Wordpress SVN" % (self.plugin_name)
        self.run_command(['svn', 'export', svn_url,
            os.path.join(self.target_location, self.plugin_name)])

"""
Creates the wpm meta directory, and downlods the list of available plugins.
"""
class DBInstaller(BaseInstaller):

    def install(self):

        data = self.download_data(self.plugins_svn)

        try:
            os.mkdir(self.wpm_meta_path)
        except OSError:
            print "WPM meta directory already exists (%s). Continuing"

        local = open(self.plugin_db_path, 'w+')

        existing_contents = list(local.read())

        plugins = re.findall('">(.*)/</a>',data)

        local.seek(0)
        local.write("\r\n".join(plugins))

        local.close()
