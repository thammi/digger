#!/usr/bin/env python
###############################################################################
##
## digger - Digging into some data mines
## Copyright (C) 2010  core
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


#should parse bitlebee-log-file to json

import datetime
import json
import re

NICK = "core"
JSONDUMP = "raw_log.json"

DATEREG = "[\d]{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"

f = open("./core.log", "r")
g = open("./raw_log.json", "w")

online_counter = 0
offline_counter = 0

data = []

for s in f:
    s = s.strip("\n")
    if s.find("core") != -1:
        timeblob = re.match(DATEREG, s)
        if s.find("+v") != -1 or s.find("has joined") != -1:
            data.append({'nick' : NICK, 'time' : timeblob.group(0), 'action' : 'online'})
            online_counter += 1
        elif s.find("-v") != -1 or s.find("quit") != -1:
            data.append({'nick' : NICK, 'time' : timeblob.group(0), 'action' : 'offline'})
            offline_counter += 1

json.dump(data, g)
f.close

print "%i online entrys and %i offline entrys found" % (online_counter, offline_counter)
