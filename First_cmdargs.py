'''
Created on Apr 26, 2013

@author: malodp
'''

from xml.dom.minidom import parseString


file = open('pom.xml','r')
data = file.read()
file.close()

dom = parseString(data)

#print dom

xmlTag = dom.getElementsByTagName('modules')[0].toxml()
print xmlTag


