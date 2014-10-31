'''
Created on Oct 23, 2013
'''

blacklisted_modules = ['os',
                       'socket',
                       'django',
                       'sqlite',
                       'thread',
                       'threading',
                       #'multiprocessing',
                       'sqlite3',
                       'urllib',
                       'urllib2',
                       'httplib',
                       'httplib2',
                       'popen2',
                       'trace',
                       'virtualenv',
                       #'sys'
                       ]

def seal():
    import sys
    for m in blacklisted_modules:
        #print "unsetting ", m
        sys.modules[m] = None

    open = None
