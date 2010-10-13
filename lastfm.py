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

import os
import json
import urllib
from warnings import warn

from json_batch import save_batch

env_var = 'LASTFM_KEY'
if env_var in os.environ:
    API_KEY = os.environ[env_var]
else:
    API_KEY = ''
    warn("No last.fm API key set, use " + env_var)

# TODO: poor stack ...
# TODO: we are missing tracks if the user is scrobbling while we fetch
def get_scrobbles(user, count=200, page=1, max_pages=500, tries=3):
    print "Fetching page", page

    query = urllib.urlencode({
        'format': 'json',
        'method': 'user.getRecentTracks',
        'api_key': API_KEY,
        'user': user,
        'limit': count,
        'page': page,
        })

    base_url = "http://ws.audioscrobbler.com/2.0/"

    try:
        res = urllib.urlopen("%s?%s" % (base_url, query))
    except IOError:
        warn("Exception while fetching the page")
        if tries > 1:
            # retry
            return get_scrobbles(user, count, page, max_pages, tries-1)
        else:
            # give up
            warn("No more tries left, aborting")
            return []

    if res.getcode() < 300:
        raw = json.load(res)

        if 'error' in raw:
            print "Error: " + raw['message']
            return []

        base = raw['recenttracks']
        scrobbles = base['track']
        pages = int(base[u'@attr']['totalPages'])

        if max_pages > 1 and page < pages:
            scrobbles.extend(get_scrobbles(user, count, page+1, max_pages-1))

        return scrobbles
    else:
        print "Unable to fetch: %i '%s'" % (res.getcode(), res.info())
        return []

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print "Please specify at least one user id"
        sys.exit(1)
    else:
        users = sys.argv[1:]

        for user in users:
            print "===> Fetching %s" % user

            dents = get_scrobbles(user)

            if not dents:
                print "ERROR: No results!"
            else:
                save_batch(user, dents, "raw_scrobbles.json")

                print "Amount of scrobbles:  %i" % len(dents)
                print

