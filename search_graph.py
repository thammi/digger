#!/usr/bin/env python
###############################################################################
##
## digger - Digging into some data mines
## Copyright (C) 2010  Thammi
## 
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU Affero General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Affero General Public License for more details.
## 
## You should have received a copy of the GNU Affero General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.
##
###############################################################################

from os.path import join
from microblogging import *
from test import *

def search_date(update):
    # splitting into time and timezone
    #print "[[[%s]]]" % commit
    time_str = update['created_at'][:-6]
    tz_str = update['created_at'][-5:]

    # calculating raw time
    strf = "%a, %d %b %Y %H:%M:%S"
    stime = time.strptime(time_str, strf)
    stamp = calendar.timegm(stime)

    # determine timezone delta
    hours = int(tz_str[1:3])
    minutes = int(tz_str[3:5])
    tz_delta = timedelta(hours=hours, minutes=minutes)
    if tz_str[0] == '+':
        tz_delta *= -1

    return datetime.fromtimestamp(stamp) + tz_delta

def main(argv):
    query = argv

    updates = []

    for service in available_services():
        print "Searching in '%s'" % service
        updates.extend(search(service, ' '.join(query)))

    path = join('search', '_'.join(query))

    blob_graph(updates, path, search_date)

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])

