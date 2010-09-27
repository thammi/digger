#!/usr/bin/env python

import sys
import json
import urllib
from warnings import warn

from json_batch import save_batch

def get_dents(user, count = 200, page = 1):
    print "Fetching page", page

    query = urllib.urlencode({
        'page': page,
        'count': count,
        'id': user
        })

    base_url = "http://identi.ca/api/statuses/user_timeline.json"

    res = urllib.urlopen("%s?%s" % (base_url, query))

    if res.getcode() < 300:
        dents = json.load(res)

        if len(dents) == count:
            dents.extend(get_dents(user, count, page + 1))

        return dents
    else:
        print "Unable to fetch: %i '%s'" % (res.getcode(), res.info())
        return None

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Please specify at least one user id"
        sys.exit(1)
    else:
        users = sys.argv[1:]

        for user in users:
            print "===> Fetching %s" % user

            dents = get_dents(user)

            if not dents:
                print "ERROR: No results!"
            else:
                save_batch(user, dents, "raw_dents.json")

                print "Amount of dents:  %i" % len(dents)
                print

