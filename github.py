#!/usr/bin/env python

import sys
import json
import re
import urllib
from warnings import warn

from json_batch import save_batch

class ServiceFailedException(Exception):

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

def api_call(method, repo, options={}):
    base_url = "http://github.com/api/v2/json/"
         
    url_parts = {
        'query' : urllib.urlencode(options),
        'base_url': base_url,
        'method': method,
        'repo' : repo
        }

    res = urllib.urlopen("{base_url}{method}/{repo}?{query}".format(**url_parts))

    if res.getcode() < 300:
        return json.load(res)
    # TODO fix end of listing
    else:
        msg = "Unable to fetch: %i" % res.getcode()
        raise ServiceFailedException(msg)
        
def fetch_repo(user, repo, branch='master'):
    #step = 200
    page = 1
    commits = []

    repo_id = '/'.join((user, repo, branch))

    # how many dents are there?
    #count = api_call('users/show', {'id': user})['statuses_count']

    while True:
        print "Fetching page %i" % page

        # fetch them
        new_commits = api_call("commits/list", repo_id, {'page': page})

        # update the count
        count = len(new_commits['commits'])

        # save the commits
        commits.extend(new_commits['commits'])
        
        if count < 35:
            break

        # next page
        page += 1

    return commits

def fetch_user():
    raise NotImplementedError

if __name__ == '__main__':
    batch_fn = "raw_github_commits.json"

    if len(sys.argv) < 2:
        print "Please specify at least one repository (user/repository/branch)"
        sys.exit(1)
    elif len(sys.argv) < 3:
        user = sys.argv[1]

        batch = fetch_user(user)

        update_batch(batch, batch_fn)
    else:
        user = sys.argv[1]
        repo = sys.argv[2]
        branch = sys.argv[3] if len(sys.argv) >= 4 else 'master'

        commits = fetch_repo(user, repo, branch)

        if not commits:
            print "ERROR: No results!"
        else:
            save_batch(repo, commits, batch_fn)

            print "Amount of commits:  %i" % len(commits)
            print

