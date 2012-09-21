#! /usr/bin/env python
from optparse import OptionParser
import sys, os, re, zipfile, shutil, urllib2, urllib, subprocess, re, tempfile, urlparse

class BaseInstaller(object):
    wpm_meta_path = os.path.expanduser('~/.wpm/')
    plugin_db_path = os.path.join(wpm_meta_path, 'available_plugins')
    tmp_dir = tempfile.mkdtemp()
    plugins_svn = "http://plugins.svn.wordpress.org"
 


    def __init__(self, *args, **kwargs):
        
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        self.set_install_location()
        
        
    """
    Sets and verifies the install path
    """
    def set_install_location(self, suffix=None):

        if hasattr(self, self.arguments[-1]) or self.is_plugin( self.arguments[-1] ):
            basepath = os.getcwd()
        else:
            basepath = os.path.abspath(self.arguments[-1])

        if suffix is not None:
            basepath = os.path.join(basepath, suffix)

        try:
            print "Setting target location"
            os.makedirs(basepath)
        except OSError:
            print "Install Location already exists. Continuing."

        self.target_location = basepath

    """
    Common method to download a file from a given url
    """        
    def download_file(self, url):
        data = self.download_data(url)
        local = open( os.path.join(self.tmp_dir, url.split('/')[-1]), 'w')
        local.write(data)
        local.close()        
        return os.path.join(self.tmp_dir, url.split('/')[-1])
        
    
    def download_data(self, url):

        conn = urllib2.urlopen(url)

        data = ""

        file_size_dl = 0
        block_sz = 500
        while True:
            buffer = conn.read(block_sz)
            if not buffer:
                break

            file_size_dl += len(buffer)
            data += buffer
            status = "Downloaded %s bytes" % (file_size_dl)
            status = status + chr(8)*(len(status)+2)
            print status,

        return data
    
        
    """
    Unzip a plugin in .zip format
    """        
    def extract(self, file):
        print "\r\nUnzipping ..."
        z = zipfile.ZipFile(file)
        z.extractall(self.tmp_dir)
        return os.path.join(self.tmp_dir, z.namelist()[0])
        
    """
    Checks to see if the plugin is in our list of plugins
    """
    def is_plugin(self, plugin_name):

        try:
            file = open( self.plugin_db_path, 'w+')
        except IOError:
            print "Couldn't open plugin database. Do you need to run wpm setup first?"
            return False

        for line in file.readlines():
            if line.strip() == plugin_name: return True

        return False
        
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
    def move_tmp(self, plugin_name):

        try:
            os.system('mv %s %s' % (os.path.join(self.tmp_dir, plugin_name), os.path.join(self.target_location, plugin_name) ))
        except OSError:
            print "Plugin %s already exists. Please remove it first." % plugin_name
            
            
    """
    Sets and verifies the install path
    """
    def set_location(self, suffix=None):

        if hasattr(self, self.args[-1]) or self._is_plugin( self.args[-1] ):
            basepath = os.getcwd()
        else:
            basepath = os.path.abspath(self.args[-1])

        if suffix is not None:
            basepath = os.path.join(basepath, suffix)

        try:
            print "Setting target location"
            os.makedirs(basepath)
        except OSError:
            print "Install Location already exists. Continuing."

        self.target_location = basepath
            
            

class ZIPInstaller(BaseInstaller):
    
    def __init__(self, *args, **kwargs):
        super(ZIPInstaller, self).__init__(*args, **kwargs)

    def install(self):
        file = self.download_file( self.url )
        plugin_path = self.extract(file)
        self.move_tmp( plugin_path.rstrip('/').split('/')[-1] )


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
        assert False, self.target_location
        self._run_command(['svn','export', url, self.target_location ])
        

        
"""
Download and extract the specified plugin from the
official WordPress plugin repository
"""
class WPInstaller(BaseInstaller):

    def install(self):
        
        if not self.is_plugin( self.plugin_name ):
            print "Invalid plugin name. If you're sure it exists, try running update."
            return
        
        svn_url = '/'.join([self.plugins_svn,self.plugin_name.replace("\n",''),'trunk'])
        print "Exporting %s from Wordpress SVN" % (self.plugin_name)
        self.run_command(['svn', 'export', svn_url, self.tmp_dir+'/'+self.plugin_name ])
        
        self.move_tmp( self.plugin_name )
        
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
            


    