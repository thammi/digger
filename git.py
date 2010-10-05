#!/usr/bin/env python

from dulwich.repo import Repo
from os.path import join, split, exists, isdir
from os import listdir

def import_dir(path):
    if exists(join(path, '.git')):
        # repo found
        return {split(path)[1]: import_repo(path)}
    else:
        # keep searching
        found = {}

        for file_name in listdir(path):
            file_path = join(path, file_name)

            if isdir(file_path):
                found.update(import_dir(file_path))

        return found

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

def import_repo(path):
    repo = Repo(path)
    commits = []

    for commit in commit_iterator(repo):
        commits.append({
            'committer': commit.committer,
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
        path = sys.argv[1]

        repo_commits = import_dir(path)

        if not repo_commits:
            print "ERROR: No results!"
        else:
            update_batch(repo_commits, "raw_git.json")

            print "Found repositories: " + ', '.join(repo_commits.keys())

