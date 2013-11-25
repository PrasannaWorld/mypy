'''
Created on Apr 29, 2013

@author: malodp
'''

import sys,re

def main():
    
    find('ig','igggg')
    
    
def find(pat, text):
    match = re.search(pat, text)
    if match: 
        print match.group()
    else:
        print "not found"
    




    
if __name__ == "__main__":
    main()
    