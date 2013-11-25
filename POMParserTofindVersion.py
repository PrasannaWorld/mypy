#!/usr/bin/python
'''
Created on Apr 26, 2013
@author: malodp@emc.com

'''

from xml.dom import minidom
import os, sys, getopt, re

DEBUG = 0
module_list = []
### This is used for testing few cases
#WORKSPACE = "C:\\viewsvn\\MoonRaker\\SRM-main\\base\\discovery\\tcn"
#WORKSPACE = "C:\\viewsvn\\MoonRaker\\SRM-main\\base\\discovery\\tcn"
#WORKSPACE = "/emc/cmgbuild/Prasanna/MoonRaker/base/discovery"
#WORKSPACE = "/emc/cmgbuild/Prasanna/MoonRaker/common/model/schemas"
#WORKSPACE = "/emc/cmgbuild/Prasanna/MoonRaker/common/tracing"
#WORKSPACE = "/emc/cmgbuild/Prasanna/MoonRaker/build"
inputfile = ''
outputfile = ''
project = ''
RELSPACE= "C:\\viewsvn\\MoonRaker\\SRM-rleng"
pat = 'ProSphere-AppDiscoveryServerUIDatasource'

def find(pat, text):
    match = re.search(pat, text)
    if match: 
        print match.group()
      
    else:
        print "not found"
    
def find_pat(pat, line):
    if re.match(pat,line):
        #print line
        vals = line.split(',')
       # print "first two values of searched string:", vals[0:2]
   
def main(argv): #{
     
    try:
        opts, args = getopt.getopt(argv, "hi:s:",["ifile="])
        #print opts
    except getopt.GetoptError:
        print 'POMParserTofindVersion.py -i <pom.xml>'
        sys.exit(2)
### Looping through the options
    for opt, arg in opts:
        if opt == 'h':
            print 'test.py -i <inputfile>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        
   # print "InPut file : ",inputfile
	XMLParser(inputfile)
#}

def findModule(project):
    if DEBUG:
        print "Project ref val:",project
    modules = project.getElementsByTagName('module')
    return(modules)

def findDepedeciesver(project):
    depverfnd = 0
    if DEBUG:
        print project
    deps = project.getElementsByTagName('dependency')
    
    if DEBUG:
        print "Dependecy in main pom (is Object array):", deps
    
    for dep in deps:
        nodes = dep.childNodes
        for child in nodes:
            if child.nodeName == 'version':
			print 'VersionFound in componet pom: ',inputfile,child.firstChild.data
			depverfnd =+1
    if  depverfnd == 0:
	 print 'VersionnotFound component pom file' 


def XMLParser(inputfile): #{    
    counter = 0
    pwd = os.getcwd()
    if DEBUG:
        print "Current Working Dir:",pwd
    
   # chdir = os.chdir(WORKSPACE)
    pwd = os.getcwd()
   
### Reading the current directory pom.xml  
       
    xmldoc = minidom.parse(inputfile) 
    project = xmldoc.getElementsByTagName('project')[0]
    
### Checking for Module Tags in pom.xml
    #modules = project.getElementsByTagName('module')
    modules = findModule(project)
   
### Checking for Dependecy tag in pom/xml  
    #deps = project.getElementsByTagName('dependency')
    findDepedeciesver(project)
    
    ''' 
    print "Dependecy in main pom (is Object array):", deps
    
    for dep in deps:
        nodes = dep.childNodes
        for child in nodes:
            if child.nodeName == 'version':
                    print 'Version Found in file :',inputfile,'->',child.firstChild.data
    ''' 
    moddepverfnd = 0 
    mod = 0
    for module in modules:
	mod =+1 
        #print 'Module :',  module ## I am listing all the object of the module (DOM elements)
        module_name = module.firstChild.data
        
        if DEBUG:
            print "Module name in pom.xml : ", module_name
        counter +=1
        
        module_list.append(module_name)
        
        if DEBUG:
            print "Changed the directory",module_name
	pathname = "%s/%s" %(cwd,module_name)	
        os.chdir(pathname)
        #os.system('cat pom.xml')
        pomdoc = minidom.parse('pom.xml')
        pomproject = pomdoc.getElementsByTagName('project')[0]
        
   
        dependencies = pomproject.getElementsByTagName('dependency')
        for dependency in dependencies:
            #print dependency
           
            childnodes = dependency.childNodes
           # print childnodes
            #print module_name,"---" 
            for child in childnodes:
              #print "Child Node : ", child
                if child.nodeName == 'version':
                    	print 'VersionFound in componet modules(',module_name,'):',child.firstChild.data
			moddepverfnd =+1
                
         
        #os.chdir('..')
		os.chdir(cwd)
        
    if (moddepverfnd == 0):
	print 'VersionnotFound in Modules'   
    
    if DEBUG:
        print "Number of modules in this pom :", counter
    if DEBUG:
        print "Module list :", module_list  
    #}



if __name__ == "__main__":
    main(sys.argv[1:])
    
