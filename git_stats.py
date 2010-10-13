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

import json
from datetime import date

def date_to_week(date_l):
    return date(*date_l[:3]).isocalendar()[:2]

def date_to_weekday(date_l):
    return date(*date_l[:3]).weekday()

class Base:
    
    def __init__(self, file_name="raw_swt.json"):
        f = file(file_name)
        self.data = data = json.load(f)
        f.close()

        # finding groups
        self.groups = groups = {}
        for raw_group in data:
            groups[str(raw_group['group'])] = Group(raw_group)

    def find_user(self, user):
        for raw_group in self.data:
            for commit in raw_group['commits']:
                if commit['author'] == user:
                    yield commit

    def commits(self):
        for group in self.groups.values():
            for commit in group.commits():
                yield commit

    def subs(self):
        return self.groups

class Group:

    def __init__(self, group_data):
        self.group_data = group_data

        self.users = users = {}
        for commit in group_data['commits']:
            name = commit['author']
            if name not in users:
                users[name] = User(name, group_data)

    def commits(self):
        return self.group_data['commits']
    
    def subs(self):
        return self.users

class User:

    def __init__(self, name, group_data):
        self.group_data = group_data
        self.name = name

    def commits(self):
        commits = self.group_data['commits']
        return (commit for commit in commits if commit['author'] == self.name)
    
    def subs(self):
        return {}
