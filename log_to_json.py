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

i = 0

for s in f:
    s = s.strip("\n")
    if s.find("core") != -1:
        timeblob = re.match(DATEREG, s)
        if s.find("+v"):
            json.dump({'nick' : NICK, 'time' : timeblob.group(0), 'action' : '+v'}, g)

        i += 1
f.close

print "%i entrys written" % i
