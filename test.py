#!/usr/bin/env python

from datetime import datetime, date, timedelta
import time
import calendar
import json
import os.path
import os

from graphs import *
from git_stats import Base, date_to_weekday
from datehelper import iso_to_gregorian

def transform_batch(batch, key):
    keys = set()
    for data in batch.itervalues():
        for item in data:
            keys.add(key(item))

    new_batch = {}
    for cur in keys:
        items = []
        for data in batch.itervalues():
            items.extend(item for item in data
                    if key(item) == cur)
        new_batch[cur] = items

    return new_batch

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

def stats_file(dates, file_name):
    out = file(file_name, 'w')

    def write(key, value):
        out.write('{0:15} {1}\n'.format(key + ":", str(value)))

    exists = (max(dates) - min(dates)).days + 1

    write("Amount", len(dates))
    write("Exists (days)", exists)
    write("Average", len(dates) / exists)

    out.close()

def blob_graph(data, target_dir, blob_to_date, blob_filter=None):
    if len(data) == 0:
        return

    if blob_filter:
        data = filter(blob_filter, data)
        dates = [blob_to_date(blob) for blob in data if blob_filter(blob)]
    else:
        dates = map(blob_to_date, data)

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    def build_path(file_name):
        return os.path.join(target_dir, file_name)

    # statistics
    stats_file(dates, build_path("stats.txt"))

    # punchcard
    def punch_date(dt):
        return (dt.hour, dt.weekday())

    agg = aggre_count(dates, punch_date)

    agg_punch_file(agg, build_path("punch_week.svg"))

    # week curve
    def week_date(dt):
        week = dt.isocalendar()[:2]
        return date2num(iso_to_gregorian(*week))

    agg = aggre_count(dates, week_date)

    agg_curve_file(agg, build_path("curve_week.png"))

    # daily curve
    def day_date(dt):
        return date2num(datetime(*dt.timetuple()[:3]))

    agg = aggre_count(dates, day_date)

    agg_curve_file(agg, build_path("curve_day.png"))

    # monthly curve
    def month_date(dt):
        year, month = dt.timetuple()[:2]
        return date2num(datetime(year, month, 1))

    agg = aggre_count(dates, month_date)

    agg_curve_file(agg, build_path("curve_month.png"))

    # punchcard over single hour/day pairs
    # aka hour/day pairs with activity (no matter how much)
    def hour_day_date(dt):
        return (dt.hour, dt.timetuple()[:3])

    def hour_day_to_week(hd):
        hour, date = hd
        return (hour, datetime(*date).weekday())

    # find hour/day tuples
    day_agg = aggre_count(dates, hour_day_date)
    # transform to hour/weekday tuples
    week_agg = aggre_count(day_agg.keys(), hour_day_to_week)

    agg_punch_file(week_agg, build_path("punch_week_single.svg"))

    agg = aggre_count(dates).keys()

    f = file(os.path.join(target_dir, "roll.png"), 'w')
    roll_date_time(agg, f)
    f.close()

def batch_graphs(batch, target_dir, blob_to_date, blob_filter=None):
    for name, data in batch.iteritems():
        item_dir = os.path.join(target_dir, name)
        blob_graph(data, item_dir, blob_to_date, blob_filter)

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

def github_date(commit):
    # splitting into time and timezone
    time_str = commit['committed_date'][:-6]
    tz_str = commit['committed_date'][-6:]

    # calculating raw time
    strf = "%Y-%m-%dT%H:%M:%S"
    stime = time.strptime(time_str, strf)
    stamp = calendar.timegm(stime)

    # determine timezone delta
    hours, minutes = (int(value) for value in tz_str[1:].split(':'))
    tz_delta = timedelta(hours=hours, minutes=minutes)
    if tz_str[0] == '+':
        tz_delta *= -1

    return datetime.fromtimestamp(stamp) + tz_delta

def json_loader(file_name):
    def loader():
        inp = file(file_name)
        batch = json.load(inp)
        inp.close()
        return batch

    return loader

def item_aspect(aspect_fun):
    return lambda batch: transform_batch(batch, aspect_fun)

def direct_aspect(batch):
    return batch

data_sources = {
        'github': {
                'load': json_loader("raw_github_commits.json"),
                'date': github_date,
                'aspects': {
                    'project': direct_aspect,
                    'user': item_aspect(lambda commit: commit['committer']['name'].lower()),
                    }
            },
        'dvcs': {
                'load': json_loader("raw_dvcs.json"),
                'date': lambda c: datetime.fromtimestamp(c['time']),
                'aspects': {
                    'project': direct_aspect,
                    'user': item_aspect(lambda commit: commit['committer'].lower()),
                    }
            },
        'log': {
                'load': lambda: {'core': json_loader('raw_log.json')},
                'filter': lambda entry: entry['action'] == 'online',
                'date': log_date,
                'aspects': {
                    'user': direct_aspect,
                    }
            },
        'identica': {
                'load': json_loader("raw_updates_identica.json"),
                'date': microblogging_date,
                'aspects': {
                    'user': direct_aspect,
                    }
            },
        'twitter': {
                'load': json_loader("raw_updates_twitter.json"),
                'date': microblogging_date,
                'aspects': {
                    'user': direct_aspect,
                    }
            },
        'lastfm': {
                'load': json_loader("raw_scrobbles.json"),
                'date': lambda s: datetime.fromtimestamp(int(s['date']['uts'])),
                'filter': lambda s: 'date' in s,
                'aspects': {
                    'user': direct_aspect,
                    }
            },
    }

def plot_source(argv):
    if len(argv) < 1:
        print "Add at least one source to plot"
        return

    for source_id in argv:
        print "==> Plotting '%s'" % source_id
        source = data_sources[source_id]

        source_path = os.path.join("out", source_id)
        date_fun = source['date']
        aspects = source['aspects']


        print "Loading source ..."

        batch = source['load']()

        for name, aspect in aspects.iteritems():
            # where to write to?
            if len(aspects) <= 1:
                # let's stay flat
                aspect_path = source_path
            else:
                # build structure
                aspect_path = os.path.join(source_path, name)

            # is there a filter defined?
            blob_filter = source['filter'] if 'filter' in source else None

            print "Generating aspect '%s' ..." % name
            aspect_batch = aspect(batch)

            print "Building '%s' graphs ..." % name
            batch_graphs(aspect_batch, aspect_path, date_fun, blob_filter)

def main(argv):
    actions = {
            'plot': plot_source,
            'curve': curve,
            'punchcard': punchcard,
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


