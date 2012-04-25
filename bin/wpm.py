#!/usr/bin/python
from optparse import OptionParser
import sys, os, re, zipfile
import urllib2
import pysvn


class WPM(object):
    wp_latest = "http://wordpress.org/latest.zip"
    plugins_svn = "http://plugins.svn.wordpress.org"
    

    def __init__(self):
        self.parser = OptionParser()        
        
    
    def main(self):
        self.set_options()
        self.options, self.args = self.parser.parse_args()
        
        getattr(self,sys.argv[1])() 
    
    def set_options(self):
        self.parser.add_option("-l", "--location", metavar="DIR", help="The location to save the file to", default=os.getcwd())
        
    def installframework(self):
        location = self.options.__dict__.get('location')
        latest = urllib2.urlopen(self.wp_latest)
        info = latest.info()
        file_name = str(re.search('filename=(.*).zip',str(info)).group(1))
        print "Downloading %s" % (file_name)
        
        local = open(''.join([location,'/',file_name,'.zip']), 'w')
        
        file_size_dl = 0
        block_sz = 8192
        while True:
            buffer = latest.read(block_sz)
            if not buffer:
                break

            file_size_dl += len(buffer)
            local.write(buffer)
            status = "Downloaded %s bytes" % (file_size_dl)
            status = status + chr(8)*(len(status)+1)
            print status,

        local.close()
              
        print "\r\nExtracting ..."
        z = zipfile.ZipFile(''.join([location,'/',file_name,'.zip']))
        z.extractall(location)
        print "Deleting zip file"
        os.remove(''.join([location,'/',file_name,'.zip']))
        print "Done"
        
    def install(self):
        import pysvn
        
        
    def search(self):
        """
        Will search for available Wordpress Packages
        """
        local = self._get_plugin_database()
        search_str = sys.argv[2]
        
        for line in local.readlines():
            if re.search(search_str, line): print line.replace("\r\n",'')
            
    def list(self):
        """
        Will list installed packages
        """
        pass

    def update(self):
        """
        Updates the list of available Wordpress Plugins
        """ 
        
        print "Getting plugins list"
        svn = urllib2.urlopen(self.plugins_svn)
        
        local = self._get_plugin_database()
        existing_contents = list(local.read())
        
        new_list = ""
    
        file_size_dl = 0
        block_sz = 500
        while True:
            buffer = svn.read(block_sz)
            if not buffer:
                break

            file_size_dl += len(buffer)
            new_list += buffer
            status = "Got %s bytes of plugins list" % (file_size_dl)
            status = status + chr(8)*(len(status)+1)
            print status,

        plugins = re.findall('">(.*)/</a>',new_list)

        local.seek(0)
        local.write("\r\n".join(plugins))
        
        local.close()
        print "\r\nDone"
        
        
    def _get_plugin_database(self):
        return open(os.path.expanduser('~/.wpm/available_plugins'), 'r')
    

if __name__ == '__main__':
    wpm = WPM()
    wpm.main()
