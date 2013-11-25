'''
Created on Apr 27, 2013

@author: malodp
'''



#for each_module in module_list:
    chdir = os.chdir(module_name)
    pwd=os.getcwd()

    print pwd
#print 'Prasanna'

    pomxmldoc = minidom.parse("pom.xml") 
    pomproject = pomxmldoc.getElementsByTagName('project')[0]
    print pomproject
    os.system('cat pom.xml')


               
                    
           
            '''
            grp_id = dependency.getElementsByTagName('groupId')[0]
            grp_name = grp_id.firstChild.data
            print grp_name
            '''
            
            #version_val = version.firstChild.data
            #print version_val 
            #"""
    
    
    group_id = dependency.getElementsByTagName('groupId')[0]
            artifactId = dependency.getElementsByTagName('artifactId')[0]
            version = dependency.getElementsByTagName('version')[0]
            
            print group_id
            groupId_val =  group_id.firstChild.data
            print groupId_val
            
            print artifactId
            artifactId_val = artifactId.firstChild.data
            print artifactId_val
            
            print version
            version_val = version.firstChild.data
            print version_val
    ===============================     
 ''' >>> This is one of the  option
    with open("C:\\viewsvn\\MoonRaker\\SRM-rleng\\Prosphere_Components_Data.list") as f:
        lines = f.read().splitlines()
        
        for line in lines:
            print line
    '''           