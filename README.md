wordpress-package-manager
=========================

A command line toolbox to help manage Wordpress dependencies.

##Getting started:

pip install wpm

wpm setup

You're all done!

Usage: wpm installframwork|install|search|update <plugin name> <location> [options]

##Command reference:

###wpm installframework

Downloads the and unpacks the latest version of Wordpress.

###wpm installplugin [plugin name==X.X.X] or [-r FILE ]

Downloads and unpacks the plugin with the given plugin name. If a requirements file is specified, it will install all plugins listed in that file.

The requirements file takes a similar format as pip: Example:

w3-total-cache
git+git://github.com/ryanbagwell/Wordpress-Weddings.git#wordpress-weddings
svn+http://plugins.svn.wordpress.org/tinymce-advanced#tinymce-advanced

###wpm search <i>search string</i>

Searches the WordPress plugin repository for plugins matching the given search string

###wpm update

Updates the latest packages from the official WordPress repository

###wpm setup

Sets up key files

##More details

Upon setup, WPM creates a .wpm directory in the user's home directory
