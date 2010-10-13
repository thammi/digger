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

