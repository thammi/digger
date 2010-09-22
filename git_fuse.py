#!/usr/bin/env python

#    Copyright (C) 2006  Andrew Straw  <strawman@astraw.com>
#
#    This program can be distributed under the terms of the GNU LGPL.
#    See the file COPYING.
#

import os, stat, errno
import fuse
from fuse import Fuse
from StringIO import StringIO
from datetime import datetime

from datehelper import iso_to_gregorian

from git_stats import *
from graphs import *

if not hasattr(fuse, '__version__'):
    raise RuntimeError, \
        "your fuse-py doesn't know of fuse.__version__, probably it's too old."

fuse.fuse_python_api = (0, 2)

hello_path = '/hello'
hello_str = 'Hello World!\n'

class MyStat(fuse.Stat):

    def __init__(self):
        self.st_mode = 0
        self.st_ino = 0
        self.st_dev = 0
        self.st_nlink = 0
        self.st_uid = 0
        self.st_gid = 0
        self.st_size = 0
        self.st_atime = 0
        self.st_mtime = 0
        self.st_ctime = 0

def exec_svg(agg):
    keys = agg.keys()
    data = [(key, agg[key]) for key in keys]

    buf = StringIO()
    punch_svg(data, buf)

    return buf.getvalue()

def exec_curve(agg):
    keys = agg.keys()
    keys.sort()

    values = [agg[key] for key in keys]

    data = (keys, values)

    buf = StringIO()
    line_plot(data, buf)
    return buf.getvalue()

def curve_day(blob):
    commits = blob.commits()
    agg = aggre_count(commits, lambda c: date2num(datetime(*c['date'][:3])))
    return exec_curve(agg)

def curve_week(blob):
    def commit_to_week_num(commit):
        week = date_to_week(commit['date'])
        greg_date = iso_to_gregorian(*week)
        return date2num(greg_date)

    commits = blob.commits()
    agg = aggre_count(commits, commit_to_week_num)
    return exec_curve(agg)

def week_punchcard(blob):
    commits = blob.commits()
    agg = aggre_count(commits, lambda c: (c['date'][3], date_to_weekday(c['date'])))
    return exec_svg(agg)

class Cache:

    def __init__(self):
        self.data = {}

    def contains(self, path):
        data = self.data
        return path in data and data[path][1]

    def insert(self, data, path):
        self.data[path] = [len(data), data, None]

    def get_size(self, path):
        return self.data[path][0]

    def get_payload(self, path):
        return self.data[path][1]

    def sweep(self):
        # TODO: sweep old items!
        pass

class ProjectFS(Fuse):

    ACTION_HOOKS = {
            'punch_week.svg': week_punchcard,
            'curve_day.png': curve_day,
            'curve_week.png': curve_week,
            }

    def __init__(self, base, *args, **kw):
        self.base = base
        Fuse.__init__(self, *args, **kw)

        # elephant-caching
        self.cache = Cache()

    def _create_data(self, path):
        blob_path, action_path = path.rsplit("/", 1)

        blob = self._get_blob(blob_path)
        data = self.ACTION_HOOKS[action_path](blob)

        self.cache.insert(data, path)

        return data

    def _get_blob(self, path):
        cur = self.base

        for element in path[1:].split('/'):
            if element:
                subs = cur.subs()
                if element in subs:
                    cur = subs[element]
                else:
                    return None

        return cur

    def getattr(self, path):
        st = MyStat()
        if path == '/':
            st.st_mode = stat.S_IFDIR | 0755
            st.st_nlink = 2
        elif path.split('/')[-1] in self.ACTION_HOOKS:
            cache = self.cache
            if not cache.contains(path):
                data = self._create_data(path)
                dlen = len(data)
            else:
                dlen = cache.get_size(path)

            st.st_mode = stat.S_IFREG | 0444
            st.st_nlink = 1
            st.st_size = dlen
        else:
            if self._get_blob(path):
                st.st_mode = stat.S_IFDIR | 0755
                st.st_nlink = 1
            else:
                return -errno.ENOENT
        return st

    def readdir(self, path, offset):
        for item in ['.', '..']:
            yield fuse.Direntry(item)

        blob = self._get_blob(path)
        if blob:
            for sub in blob.subs():
                yield fuse.Direntry(str(sub))

            for action in self.ACTION_HOOKS:
                yield fuse.Direntry(action)

    def open(self, path, flags):
        blob_path, action_path = path.rsplit("/", 1)

        if action_path not in self.ACTION_HOOKS or self._get_blob(blob_path) == None:
            return -errno.ENOENT

        accmode = os.O_RDONLY | os.O_WRONLY | os.O_RDWR
        if (flags & accmode) != os.O_RDONLY:
            return -errno.EACCES

    def read(self, path, size, offset):
        blob_path, action_path = path.rsplit("/", 1)

        if action_path not in self.ACTION_HOOKS or self._get_blob(blob_path) == None:
            return -errno.ENOENT

        cache = self.cache
        if not cache.contains(path):
            data = self._create_data(path)
        else:
            data = cache.get_payload(path)

        slen = len(data)
        if offset < slen:
            if offset + size > slen:
                size = slen - offset
            buf = data[offset:offset+size]
        else:
            buf = ''

        return buf

def main():
    usage="""
Showing off with some nice graphics

""" + Fuse.fusage

    base = Base()

    server = ProjectFS(base,
            version="%prog " + fuse.__version__,
            usage=usage,
            dash_s_do='setsingle')

    server.parse(errex=1)
    server.main()

if __name__ == '__main__':
    main()

