#!/usr/bin/env python

import sys
import json
import re
import urllib
from warnings import warn

from json_batch import save_batch

class UnknownServiceException(Exception):

    def __init__(self, service):
        self.service = service

    def __str__(self):
        return self.service

class ServiceFailedException(Exception):

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

def api_call(method, options):
    base_urls = {
            'identica' : "http://identi.ca/api/",
            'twitter' : "http://api.twitter.com/1/",
            }

    if service not in base_urls:
        raise UnknownServiceException(service)

    url_parts = {
            'query': urllib.urlencode(options),
            'base_url': base_urls[service],
            'method': method,
            }

    res = urllib.urlopen("{base_url}{method}.json?{query}".format(**url_parts))

    # watch rate limit (twitter only)
    ratelimit = re.search("X-RateLimit-Remaining: ([0-9]+)", str(res.info()))
    if ratelimit != None:
        print "remaining API-calls: %s" % ratelimit.group(1)

    if res.getcode() < 300:
        return json.load(res)
    else:
        msg = "Unable to fetch: %i" % res.getcode()
        raise ServiceFailedException(msg)
        

def get_page(service, user, count, page):
    options = {
            'page': page,
            'count': count,
            'id': user,
            'include_rts': 'true', #get all 200 tweets from twitter
            }

    return api_call('statuses/user_timeline', options)

def get_statuses(service, user, limit=None):
    step = 200
    page = 1
    statuses = []

    # how many dents are there?
    count = api_call('users/show', {'id': user})['statuses_count']

    if limit:
        count = min(count, limit)

    while count > 0:
        print "Fetching page %i, %i updates remaining" % (page, count)

        # how many statuses to fetch?
        fetch_count = min(step, count)

        # fetch them
        new_statuses = get_page(service, user, fetch_count, page)

        # update the count
        count -= len(new_statuses)

        # save the statuses
        statuses.extend(new_statuses)

        # next page
        page += 1

    return statuses

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Please specify at least the service (identica or twitter) and one user id"
        sys.exit(1)
    else:
        service = sys.argv[1]
        users = sys.argv[2:]

        for user in users:
            print "===> Fetching %s on %s" % (user, service)

            updates = get_statuses(service, user)

            if not updates:
                print "ERROR: No results!"
            else:
                save_batch(user, updates, "raw_updates_%s.json" % service)

                print "Amount of updates:  %i" % len(updates)
                print

