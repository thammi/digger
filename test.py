#!/usr/bin/env python

from datetime import datetime
import time
import calendar
import json
import os.path
import os

from graphs import *
from git_stats import Base, date_to_weekday
from datehelper import iso_to_gregorian

def paint_curve(agg):
    keys = agg.keys()
    keys.sort()

    values = [agg[key] for key in keys]

    data = (keys, values)
    #data = values

    f = file("out.png", "w")
    line_plot(data, f)
    f.close()

def paint_punchcard(commits):
    agg = aggre_count(commits, lambda c: (c['date'][3], date_to_weekday(c['date'])))

    keys = agg.keys()
    data = [(key, agg[key]) for key in keys]

    f = file("out.svg", 'w')
    punch_svg(data, f)
    f.close()

def punchcard(argv):
    b = Base()

    data = b.commits()

    paint_punchcard(data)

def curve(argv):
    b = Base()

    data = b.commits()
    #data = b.groups[25].commits()

    agg = aggre_count(data, lambda c: date2num(datetime(*c['date'][:3])))
    paint_curve(agg)

def batch_graphs(batch, target_dir, blob_to_date):
    for user, dents in batch.iteritems():
        user_dir = os.path.join(target_dir, user)

        if not os.path.exists(user_dir):
            os.makedirs(user_dir)

        # punchcard
        def punch_date(dent):
            dt = blob_to_date(dent)
            return (dt.hour, dt.weekday())

        agg = aggre_count(dents, punch_date)

        keys = agg.keys()
        data = [(key, agg[key]) for key in keys]

        out = file(os.path.join(user_dir, "punch_week.svg"), 'w')
        punch_svg(data, out)
        out.close()

        # week curve
        def week_date(dent):
            dt = blob_to_date(dent)
            week = dt.isocalendar()[:2]
            return date2num(iso_to_gregorian(*week))

        agg = aggre_count(dents, week_date)

        keys = agg.keys()
        keys.sort()
        values = [agg[key] for key in keys]
        data = (keys, values)

        out = file(os.path.join(user_dir, "curve_week.png"), 'w')
        line_plot(data, out)
        out.close()

def identi_date(dent):
    strf = "%a %b %d %H:%M:%S +0000 %Y"
    stime = time.strptime(dent['created_at'], strf)
    stamp = calendar.timegm(stime)
    return datetime.fromtimestamp(stamp)


def identica(argv):
    inp = file("raw_dents.json")
    batch = json.load(inp)
    inp.close()

    batch_graphs(batch, "dentgraph", identi_date)

def main(argv):
    actions = {
            'curve': curve,
            'punchcard': punchcard,
            'identica': identica,
            }

    if len(argv):
        action_id = argv[0]
        if action_id in actions:
            actions[action_id](argv[1:])
        else:
            print "Unknown command, use one of those:"

            for action in actions:
                print "-", action
    else:
        print "Please select a command."
        print

        print "Available:"
        for action in actions:
            print "-", action

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])


