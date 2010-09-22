#!/usr/bin/env python

from os import listdir
from os.path import split, join, isdir
import git
import sys

def load(path="data"):
    res = []
    for f in listdir(path):
        full_path = join(path, f)

        if isdir(full_path):
            res.append(load_dir(full_path))
    
    return res

def load_dir(path):
    res = {}

    dir_name = split(path)[1]
    res['group'] = int(dir_name.split('-')[1])

    res['commits'] = load_commits(path)
    #res['metrics'] = load_metrics(path)

    return res

def load_metrics(path):
    return {}

def load_commits(path):
    sys.stderr.write("[%s]\n" % path)

    repo = git.Repo(path)

    count = repo.commit_count()
    commits = repo.commits(max_count=count)

    return [read_commit(c) for c in commits]

def read_commit(commit):
    res = {}

    res['author'] = commit.author.name
    date = list(commit.authored_date)
    date[3] = (date[3] + 2) % 24
    res['date'] = date

    # TODO: crashes!!!
    # TODO: is there a better way?
    #add = 0
    #remove = 0
    #print commit
    #print commit.diffs
    #for diff in commit.diffs:
        #lines = diff.diff.split('\n')[3:]
        #for line in lines:
            #if line.startswith('+'):
                #add += 1
            #elif line.startswith('-'):
                #remove += 1

    #res['added'] = add
    #res['removed'] = remove

    return res

raw = load()

import json
print json.dumps(raw)

