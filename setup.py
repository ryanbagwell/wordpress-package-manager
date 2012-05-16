#!/usr/bin/env python
from distutils.core import setup
from distutils.command.install_data import install_data

class PostInstall(install_data):

    def run(self):
        install_data.run(self)
        proc = subprocess.Popen(['wpm', 'setup'],stdout=subprocess.PIPE)
        for line in proc.stdout:
            if line is not "\r\n": print line 
        

setup(name='Wordpress-Package-Manager',
      version='0.3',
      description='A command-line tool for installing WordPress plugins',
      long_description="A command-line tool for installing WordPress plugins in a manner similar to PIP.",
      author='Ryan Bagwell',
      author_email='ryan@ryanbagwell.com',
      url='https://github.com/ryanbagwell',
      scripts=['wpm'],
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Programming Language :: PHP',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Python Software Foundation License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
      ],
     )