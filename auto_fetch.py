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

from os.path import join, exists

from microblogging import *
from test import *

def search(service, query):
    urls = {
            'identica' : "http://identi.ca/api/search.json",
            'telecomix' : "http://status.telecomix.org/api/search.json",
            'twitter' : "http://search.twitter.com/search.json",
            }

    if service not in urls:
        raise UnknownServiceException(service)

    url_parts = {
            'query': urllib.urlencode({'q': query}),
            'url': urls[service],
            }

    res = urllib.urlopen("{url}?{query}".format(**url_parts))

    if res.getcode() < 300:
        return json.load(res)
    else:
        msg = "Unable to fetch: %i" % res.getcode()
        raise ServiceFailedException(msg)
 
def user_exists(service, user):
    return exists(user_path(service, user))

def user_path(service, user):
    return join('auto', service, user)

def main(argv):
    service = argv[0]
    tags = argv[1:]

    updates = search(service, ' '.join('#' + tag for tag in tags))['results']

    users = set(update['from_user'] for update in updates)
    users = filter(lambda u: not user_exists(service, u), users)

    print "Fetching: " + ', '.join(users)

    for user in users:
        try:
            print "==> Fetching '%s'" % user
            updates = get_statuses(service, user, 1000)

            blob_graph(updates, user_path(service, user), microblogging_date)
        except Exception as e:
            # the show must go on ...
            print e

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])

