#!/usr/bin/python
from optparse import OptionParser
import sys, os, re, zipfile
import urllib2



class WPM(object):
    wp_latest = "http://wordpress.org/latest.zip"
    plugins_svn = "http://plugins.svn.wordpress.org"
    plugin_db_path = os.path.expanduser('~/.wpm/available_plugins')
    

    def __init__(self):
        self.parser = OptionParser()        
        
    
    def main(self):
        self.set_options()
        self.options, self.args = self.parser.parse_args()
        
        getattr(self,sys.argv[1])() 
    
    def set_options(self):
        
        self.parser.add_option("-l", "--location", metavar="DIR", help="The location to save the file to", default=os.getcwd())
        self.parser.add_option("-r", "--requirements", metavar="FILE", help="The location of the requirements file", default=os.getcwd())
        
    def installframework(self):
        file = ''.join([self.options.__dict__.get('location'),'/','wordpres.zip'])
        data = self._download_data(self.wp_latest)
        local = open(file, 'w')
        local.write(data)
        local.close()
              
        self._extract(file)
        
    def install(self):
        """
        Will download and save the plugins
        """
        plugin_name = sys.argv[2]
  
        if 'requirements' in self.options.__dict__:
            file = open(self.options.__dict__.get('requirements'), 'r')
            requirements = file.readlines()
            file.close()
            
            for line in requirements:
                line = line.strip()
                
                if (line == ''): continue
            
                self._wp_svn_install(line)
                print "Installed " + line
        else:
            self._wp_svn_install(plugin_name)
        
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

        data =self._download_data(self.plugins_svn)
        local = self._get_plugin_database()
        existing_contents = list(local.read())
        
        plugins = re.findall('">(.*)/</a>',data)

        local.seek(0)
        local.write("\r\n".join(plugins))
        
        local.close()
        print "\r\nDone"
        
        
    def _get_plugin_database(self):
        return open(os.path.expanduser('~/.wpm/available_plugins'), 'r+')
        
    def _download_data(self, url):
        
        print url
        
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
            status = status + chr(8)*(len(status)+1)
            print status,
        
        return data
        
    def _extract(self,file):
        location = self.options.__dict__.get('location')
        print "\r\nExtracting ..."
        z = zipfile.ZipFile(file)
        z.extractall(location)
        print "Deleting zip file"
        os.remove(file)
        print "Done"
        
    
    def _wp_svn_install(self, plugin_name):
        download_url = "http://downloads.wordpress.org/plugin/%s.zip" % (plugin_name.replace("\n",''))
        contents = self._download_data(download_url)
        file = ''.join([self.options.__dict__.get('location'),'/',plugin_name,'.zip'])
        local = open(file, 'w')
        local.write(contents)
        local.close()
        self._extract(file)        
        
    def setup(self):

        print "Creating .wpm directory"

        try:
            os.mkdir(os.path.expanduser('~/.wpm'))
        except OSError:
            print ".wpm directory already exists."
        else:
            print "Couldn't create .wpm directory. Exiting."

        if not os.path.exists(self.plugin_db_path):
            file = open(self.plugin_db_path, 'w')
            file.write('')
            file.close()        
   
        self.update()
        
        print "Finished setup"
        

if __name__ == '__main__':
    wpm = WPM()
    wpm.main()
