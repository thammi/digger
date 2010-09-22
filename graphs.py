#!/usr/bin/env python

import Gnuplot

from projects import *
import svg

def aggre_count(commits, key):
    counter = {}
    
    for commit in commits:
        value = key(commit)
        if value in counter:
            counter[value] += 1
        else:
            counter[value] = 1

    return counter

def plot(data):
    g = Gnuplot.Gnuplot()
    g('set style data lines')
    #g('set style data linespoints')
    #g('set xrange [0:23]')
    g.plot(data)

    raw_input()

def punch_svg(data, out, size = (800, 300)):
    max_point = max(value for key, value in data)
    x_amount = max(x for (x, y), value in data) + 2
    y_amount = max(y for (x, y), value in data) + 2

    x_step = float(size[0]) / x_amount
    y_step = float(size[1]) / y_amount
    box_size = min(float(size[0])/x_amount, float(size[1])/y_amount)
    size_step = box_size / 2 * 0.8 / max_point
    font_size = box_size*0.7
    
    root = svg.SVG(size)
    root.style('fill', 'black')
    root.style('stroke', 'grey')

    caption = svg.Group()
    root.add(caption)
    caption.style('fill', 'grey')
    caption.style('font-size', font_size)
    caption.style('text-anchor', 'middle')

    # vertical captions
    for step in range(y_amount - 1):
        y = y_step * (step + 2) - (box_size - font_size) / 2
        x = x_step / 2

        caption.add(svg.Text(str(step), (x, y)))

    # horizontal captions
    for step in range(x_amount - 1):
        x = x_step * (step + 1) + x_step / 2
        y = y_step - (box_size - font_size) / 2

        caption.add(svg.Text(str(step), (x, y)))

    # painting horizontal lines
    for step in range(y_amount + 1):
        y = y_step * step
        root.add(svg.Line((0, y), (size[0], y)))

    # painting vertical lines
    for step in range(x_amount + 1):
        x = x_step * step
        root.add(svg.Line((x, 0), (x, size[1])))

    # painting the data
    for (x, y), value in data:
        x = x_step * (x + 1) + x_step / 2
        y = y_step * (y + 1) + y_step / 2
        radius = size_step * value

        root.add(svg.Circle(radius, (x, y)))

    root.write(out)

def main(argv):
    b = Base()

    #data = b.commits()
    #data = b.find_user("s2960869") # me
    data = b.find_user("s8572327") # twobit
    #data = b.find_user("s3957022") # kilian
    #data = b.find_user("s1394474") # payload
    #data = b.groups[25].commits()

    agg = aggre_count(data, lambda c: (c['date'][3], date_to_weekday(c['date'])))

    keys = agg.keys()
    data = [(key, agg[key]) for key in keys]

    f = file("out.svg", 'w')
    punch_svg(data, f)
    f.close()

    #agg = aggre_count(b.commits(), lambda c: "%s.%s" % (c['date'][1], c['date'][2]))
    #agg = aggre_count(b.commits(), lambda c: "%s.%s"%(date_to_weekday(c['date']),c['date'][3]))

    #keys = agg.keys()
    #keys.sort()

    #data = [(key, agg[key]) for key in keys]

    #plot(data)

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])

