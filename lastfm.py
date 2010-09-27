#!/usr/bin/env python

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

def get_scrobbles(user, count=200, page=1, max_pages=100):
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

    res = urllib.urlopen("%s?%s" % (base_url, query))

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

                print "Amount of dents:  %i" % len(dents)
                print

