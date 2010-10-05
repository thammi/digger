#!/usr/bin/env python

from datetime import datetime, date
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

def agg_curve_file(agg, file_name):
    keys = agg.keys()
    keys.sort()
    values = [agg[key] for key in keys]
    data = (keys, values)

    out = file(file_name, 'w')
    line_plot(data, out)
    out.close()

def agg_punch_file(agg, file_name):
    keys = agg.keys()
    data = [(key, agg[key]) for key in keys]

    out = file(file_name, 'w')
    punch_svg(data, out)
    out.close()

def batch_graphs(batch, target_dir, blob_to_date, blob_filter=None):
    for user, data in batch.iteritems():
        user_dir = os.path.join(target_dir, user)

        if blob_filter:
            data = filter(blob_filter, data)

        if not os.path.exists(user_dir):
            os.makedirs(user_dir)

        # punchcard
        def punch_date(item):
            dt = blob_to_date(item)
            return (dt.hour, dt.weekday())

        agg = aggre_count(data, punch_date)

        agg_punch_file(agg, os.path.join(user_dir, "punch_week.svg"))

        # week curve
        def week_date(item):
            dt = blob_to_date(item)
            week = dt.isocalendar()[:2]
            return date2num(iso_to_gregorian(*week))

        agg = aggre_count(data, week_date)

        agg_curve_file(agg, os.path.join(user_dir, "curve_week.png"))

        # daily curve
        def day_date(item):
            dt = blob_to_date(item)
            return date2num(datetime(*dt.timetuple()[:3]))

        agg = aggre_count(data, day_date)

        agg_curve_file(agg, os.path.join(user_dir, "curve_day.png"))

        # monthly curve
        def month_date(item):
            dt = blob_to_date(item)
            year, month = dt.timetuple()[:2]
            return date2num(datetime(year, month, 1))

        agg = aggre_count(data, month_date)

        agg_curve_file(agg, os.path.join(user_dir, "curve_month.png"))

        # punchcard over single hour/day pairs
        # aka hour/day pairs with activity (no matter how much)
        def hour_day_date(item):
            dt = blob_to_date(item)
            return (dt.hour, dt.timetuple()[:3])

        def hour_day_to_week(hd):
            hour, date = hd
            return (hour, datetime(*date).weekday())

        # find hour/day tuples
        day_agg = aggre_count(data, hour_day_date)
        # transform to hour/weekday tuples
        week_agg = aggre_count(day_agg.keys(), hour_day_to_week)

        agg_punch_file(week_agg, os.path.join(user_dir, "punch_week_single.svg"))

        # 2d graph
        def date_hour(item):
            dt = blob_to_date(item)
            return (dt.date(), dt.hour)

        data = aggre_count(data, date_hour).iterkeys()

        f = file(os.path.join(user_dir, "roll.png"), 'w')
        roll_date_time(data, f)
        f.close()

def microblogging_date(dent):
    strf = "%a %b %d %H:%M:%S +0000 %Y"
    stime = time.strptime(dent['created_at'], strf)
    stamp = calendar.timegm(stime)
    return datetime.fromtimestamp(stamp)

def log_date(entry):
    strf = "%Y-%m-%d %H:%M:%S"
    stime = time.strptime(entry['time'], strf)
    stamp = calendar.timegm(stime)
    return datetime.fromtimestamp(stamp)


def log(argv):
    inp = file("raw_log.json")
    batch = {}
    batch['core'] = json.load(inp)
    inp.close()

    batch_graphs(batch, "loggraph", log_date)

def identica(argv):
    inp = file("raw_updates_identica.json")
    batch = json.load(inp)
    inp.close()

    batch_graphs(batch, "dentgraph", microblogging_date)

def twitter(argv):
    inp = file("raw_updates_twitter.json")
    batch = json.load(inp)
    inp.close()

    batch_graphs(batch, "twitgraph", microblogging_date)

def lastfm(argv):
    inp = file("raw_scrobbles.json")
    batch = json.load(inp)
    inp.close()

    def scrobble_date(scrobble):
        return datetime.fromtimestamp(int(scrobble['date']['uts']))

    def date_filter(scrobble):
        return 'date' in scrobble

    batch_graphs(batch, "lastgraph", scrobble_date, date_filter)

def main(argv):
    actions = {
            'curve': curve,
            'punchcard': punchcard,
            'identica': identica,
            'twitter' : twitter,
            'lastfm': lastfm,
            'log' : log,
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


