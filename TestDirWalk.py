
import os

top = 'c:/viewsvn/MoonRaker/SRM-main-latest'
for dirpath, dirnames, filenames in os.walk(top):
    for filename in filenames:
        print os.path.join(os.path.abspath(filename) )
     
