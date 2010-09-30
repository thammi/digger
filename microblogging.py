#!/usr/bin/env python

import sys
import json
import re
import urllib
from warnings import warn

from json_batch import save_batch

def get_updates(service, user, count = 200, page = 1, updatescount = -1):
    if service in ["identica", "twitter"]:

        base_url = { 'identica' : "http://identi.ca/api/",
                     'twitter' : "http://api.twitter.com/1/",
                     }

        if updatescount == -1:

            query = urllib.urlencode({
                    'id': user
                    })
            
            res = urllib.urlopen("%susers/show.json?%s" % (base_url[service], query))

            userdata = json.load(res)

            updatescount = userdata['statuses_count']

        print "Fetching page %i, %i updates remaining" % (page, updatescount)

        if updatescount < 200:
            count = updatescount

        query = urllib.urlencode({
                'page': page,
                'count': count,
                'id': user,
                'include_rts': "true" #get all 200 tweets from twitter
                })

        res = urllib.urlopen("%sstatuses/user_timeline.json?%s" % (base_url[service], query))

        if service == "twitter":
            #watch rate limit
            ratelimit = re.search("X-RateLimit-Remaining: ([0-9]+)", str(res.info()))
            if ratelimit != None:
                print "remaining API-calls: %s" % ratelimit.group(1)

        if res.getcode() < 300:
            updates = json.load(res)
            
            #print "Got %i updates" % len(updates)

            if len(updates) > 0:
                if (updatescount - count > 0):
                    updates.extend(get_updates(service, user, count, page + 1, updatescount - count))
                
                return updates
            else:
                #print "Unable to fetch: %i '%s'" % (res.getcode(), res.info())
                print "Unable to fetch more tweets"
                #return None
                return []

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
                save_batch(user, updates, "raw_updates_%s.json" % service)

                print "Amount of updates:  %i" % len(updates)
                print

