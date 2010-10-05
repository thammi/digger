#!/usr/bin/env python
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
