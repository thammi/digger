#!/usr/bin/env python3

import sys
import json
import urllib
from warnings import warn
import os.path

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
        return None

def save_dents(user, dents, file_name="raw_dents.json"):
    if os.path.exists(file_name):
        # read in old dents
        try:
            inp = file(file_name)
            batch = json.load(inp)
            inp.close()
        except:
            warn("Couldn't load old dents")
            batch = {}
    else:
        batch = {}

    # insert new dents
    batch[user] = dents

    # writing back
    out = file(file_name, "w")
    json.dump(batch, out)
    out.close()

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
                print "ERROR: Unable to fetch messages!"
            else:
                save_dents(user, dents)

                print "Amount of dents:  %i" % len(dents)
                print

