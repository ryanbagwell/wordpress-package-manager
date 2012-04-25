#!/usr/bin/python
import wpm, os

if __name__ == '__main__':
    
    print "Creating .wpm directory"
    
    try:
        os.mkdir(os.path.expanduser('~/.wpm'))
    except OSError:
        print ".wpm directory already exists."
    else:
        print "Couldn't create .wpm directory. Exiting."
    
    if not os.path.exists(os.path.expanduser('~/.wpm')+'/available_plugins'):
        file = open(os.path.expanduser('~/.wpm')+'/available_plugins', 'w')
    	file.write('')
    	file.close()        
        
    
    wpm = wpm.WPM()
    wpm.update()
        
        
    