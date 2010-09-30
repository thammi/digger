#!/usr/bin/env python

import sys
import json
import urllib
from warnings import warn

from json_batch import save_batch

def get_updates(service, user, count = 200, page = 1):
    if service in ["identica", "twitter"]:
        print "Fetching page", page

        query = urllib.urlencode({
                'page': page,
                'count': count,
                'id': user
                })

        base_url = { 'identica' : "http://identi.ca/api/statuses/user_timeline.json",
                     'twitter' : "http://api.twitter.com/1/statuses/user_timeline.json",
                     }

        res = urllib.urlopen("%s?%s" % (base_url[service], query))

        if res.getcode() < 300:
            updates = json.load(res)

            if len(updates) == count:
                updates.extend(get_updates(service, user, count, page + 1))

                return updates
            else:
                print "Unable to fetch: %i '%s'" % (res.getcode(), res.info())
                return None
    else:
        print "please specify correct service (identica or twitter)"
        return None

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Please specify at least the service (identica or twitter) and one user id"
        sys.exit(1)
    else:
        service = sys.argv[1]
        users = sys.argv[2:]

        for user in users:
            print "===> Fetching %s on %s" % (user, service)

            updates = get_updates(service, user)

            if not updates:
                print "ERROR: No results!"
            else:
                save_batch(user, dents, "raw_updates_%s.json" % service)

                print "Amount of updates:  %i" % len(updates)
                print

