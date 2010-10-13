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


from mercurial import hg, ui

from dulwich.repo import Repo

from os.path import join, split, exists, isdir, islink, abspath
from os import listdir
from re import compile

def import_dir(path):
    if exists(join(path, '.git')):
        # repo found
        return build_structure(path, import_git)
    if exists(join(path, '.hg')):
        # repo found
        return build_structure(path, import_hg)
    else:
        # keep searching
        found = {}

        for file_name in listdir(path):
            file_path = join(path, file_name)

            if isdir(file_path) and not islink(file_path):
                found.update(import_dir(file_path))

        return found

def build_structure(path, fun):
    print path
    return {split(abspath(path))[1]: fun(path)}

def import_hg(path):
    repo = hg.repository(ui.ui(), path)
    commits = []

    for revision in repo:
        commit = repo[revision]
        commits.append({
            'committer': commit.user(),
            'time': commit.date()[0]
            })

    return commits

def commit_iterator(repo):
    walker = repo.get_graph_walker()

    while True:
        # what's next?
        sha = walker.next()

        if sha:
            # let's throw the commit out
            yield repo[sha]
        else:
            # we are done here
            break

user_re = compile('(.*)\s<(.*)>$')

def import_git(path):
    repo = Repo(path)
    commits = []

    for commit in commit_iterator(repo):
        match = user_re.match(commit.committer)

        commits.append({
            'committer': match.group(1),
            'mail': match.group(2),
            'time': commit.commit_time,
            'message': commit.message,
            })
    
    return commits

if __name__ == '__main__':
    import sys
    from json_batch import update_batch

    if len(sys.argv) < 2:
        print "Please specify a path"
        sys.exit(1)
    else:
        paths = sys.argv[1:]

        commits = {}

        for path in paths:
            commits.update(import_dir(path))

        if not commits:
            print "ERROR: No results!"
        else:
            update_batch(commits, "raw_dvcs.json")

            print "Found repositories: " + ', '.join(sorted(commits.keys()))

