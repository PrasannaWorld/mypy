'''
Created on Apr 26, 2013

@author: malodp
'''

import datetime as dt
"""
today = dt.datetime.now()
print today
pri2day = dt.datetime.now() - dt.timedelta(days=2)

print pri2day
"""

def last_day_of_month():
    today = dt.datetime.now()
    print today
    nm = dt.date(today.year, today.month, 15) + dt.timedelta(days=31)
    print nm
    eom = dt.date(nm.year, nm.month, 1) - dt.timedelta(days=1)
    print eom
    print eom.day
    print nm.day
    print today.day
    #return '%s %s %s' % (eom.year, eom.month, eom.day)


def main():
    last_day_of_month()



if __name__ == "__main__":
    main()
