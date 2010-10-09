#!/usr/bin/env python

from datetime import datetime, date, timedelta
import time
import calendar
import json
import os.path
import os
import re

from graphs import *
from datehelper import iso_to_gregorian

def transform_batch(batch, key):
    new_batch = {}

    for data in batch.itervalues():
        for item in data:
            cur = key(item)

            if cur in new_batch:
                new_batch[cur].append(item)
            else:
                new_batch[cur] = [item]

    return new_batch

def limit_transform(batch, key, max_amount):
    # first find out which keys are used how much
    keys = {}
    for data in batch.itervalues():
        for item in data:
            cur = key(item)
            if cur in keys:
                keys[cur] += 1
            else:
                keys[cur] = 1

    # sort them and only keep $max_amoun keys
    top = sorted(keys.iteritems(), key=lambda (k, v): v, reverse=True)[:max_amount]

    # actually move data around
    new_batch = {}
    for cur in (key for key, value in top):
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

def hashtag_transform(batch):
    hash_batch = {}
    count = 0

    hash_ex = re.compile('\W#([\w_-]+)(?:\W|$)', re.LOCALE)
    filter_ex = re.compile('_|-')

    for user in batch.itervalues():
        for message in user:
            count += 1

            tags = (filter_ex.sub('', tag.lower()) for tag
                    in hash_ex.findall(message['text']))

            for tag in tags:
                if tag not in hash_batch:
                    hash_batch[tag] = [message]
                else:
                    hash_batch[tag].append(message)

    # throw away less used tags
    threshold = max(count / 500.0, 5)
    for tag, messages in hash_batch.items():
        if len(messages) < threshold:
            del hash_batch[tag]

    # a small popularity contest ;)
    popular = sorted(hash_batch.iteritems(), key=lambda (tag, msgs): len(msgs), reverse=True)[:10]
    print "Popular Hash-Tags: " + ', '.join(tag for tag, msgs in popular)

    return hash_batch

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
    #print "[[[%s]]]" % commit
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
        if os.path.exists(file_name):
            inp = file(file_name)
            batch = json.load(inp)
            inp.close()
            return batch
        else:
            return {}

    return loader

def item_aspect(aspect_fun):
    return lambda batch: transform_batch(batch, aspect_fun)

def limited_item_aspect(aspect_fun, limit):
    return lambda batch: limit_transform(batch, aspect_fun, limit)


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
                'load': json_loader("raw_log.json"),
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
                    'hashtag': hashtag_transform,
                    }
            },
        'twitter': {
                'load': json_loader("raw_updates_twitter.json"),
                'date': microblogging_date,
                'aspects': {
                    'user': direct_aspect,
                    'hashtag': hashtag_transform,
                    }
            },
        'lastfm': {
                'load': json_loader("raw_scrobbles.json"),
                'date': lambda s: datetime.fromtimestamp(int(s['date']['uts'])),
                'filter': lambda s: 'date' in s,
                'aspects': {
                    'user': direct_aspect,
                    'artist': limited_item_aspect(lambda s: s['artist']['#text'], 50),
                    }
            },
    }

def plot_source(argv):
    if len(argv) < 1:
        print "Add at least one source to plot"
        return

    for source_id in argv:
        print "==> Plotting '%s'" % source_id

        if source_id not in data_sources:
            print "ERROR: Source '%s' not found!" % source_id
            break

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

            print "Building '%s' graphs (%i items) ..." % (name, len(aspect_batch))
            batch_graphs(aspect_batch, aspect_path, date_fun, blob_filter)

def aspect_plot(aspect_id, targets, sources=None):
    if sources == None:
        sources = data_sources.keys()

    dates = {}

    for target_id in targets:
        dates[target_id] = []

    for source_id in sources:
        print "==> Processing aspect '%s'" % source_id

        if source_id not in data_sources:
            print "ERROR: Unknown source!"
            break

        source = data_sources[source_id]

        if aspect_id in source['aspects']:
            print "Loading source ..."

            batch = source['load']()

            print "Calculating the aspect ..."

            aspect_batch = source['aspects'][aspect_id](batch)

            print "Searching the targets in the aspect ..."

            blob_filter = source['filter'] if 'filter' in source else lambda i: True
            date_fun = source['date']
            # for each target
            for target_id, aliases in targets.iteritems():
                # ... and each alias of it ...
                for alias in aliases:
                    # ... check for events
                    if alias in aspect_batch:
                        dates[target_id].extend(
                                date_fun(item)
                                for item
                                in aspect_batch[alias]
                                if blob_filter(item))
        else:
            print "Source doesn't have the searched aspect"

    print "==> Calculating the graph"

    for target_id, data in dates.iteritems():
        path = os.path.join('out', 'aspect', aspect_id, target_id)
        blob_graph(data, path, lambda date: date)

def filter_aspect(argv):
    if len(argv) < 2:
        print "Please use the following parameters: aspect_id target [alias ...]"
        return

    aspect_id = argv[0]
    targets = {
            # one target with given aliases
            argv[1]: argv[1:],
            }

    aspect_plot(aspect_id, targets)

def aspect_file(argv):
    if len(argv) < 2:
        print "Please use the following parameters: aspect_id alias_file [sources ...]"
        return

    aspect_id = argv[0]
    afile = argv[1]
    sources = argv[2:] if len(argv) > 2 else None

    if not os.path.exists(afile):
        print "The specified file doesn't exist"
        return

    targets = {}

    target_id = None
    for line in file(afile):
        line = line.strip()

        if line.startswith('[') and line.endswith(']'):
            # target ids are defined as '[$target_id]'
            target_id = line[1:-1]
            targets[target_id] = []
        elif len(line) > 0:
            # all other lines are considered aliases for the last target id
            if target_id:
                targets[target_id].append(line)
            else:
                print "Malformed alias file, no target id for entry '%s'" % line

    aspect_plot(aspect_id, targets, sources)

def main(argv):
    actions = {
            'plot': plot_source,
            'afilter': filter_aspect,
            'afile': aspect_file,
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


