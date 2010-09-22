#!/usr/bin/env python

import Gnuplot

from projects import *


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
    
    out.write('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN" "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd"><svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="%ipx" height="%ipx">\n' % size)

    out.write('<rect x="0" y="0" width="{0}" height="{1}" fill="white" />'.format(size[0], size[1]))
    out.write('<g style="fill: black; stroke: gray; font-size: {font};" text-anchor="middle">'.format(font=font_size))

    # painting some lines to enhance readability

    # painting horizontal lines
    for step in range(y_amount + 1):
        if step:
            geo = {
                    'y': y_step * (step + 1 ) - (box_size - font_size) / 2,
                    'data': step - 1,
                    'x': x_step / 2,
                    }

            out.write('<text style="fill: gray;" y="{y}" x="{x}">{data}</text>\n'.format(**geo))

        geo = {
                'x_size': size[0],
                'y': y_step * step,
                }
        out.write('<line x1="0" x2="{x_size}" y1="{y}" y2="{y}" />\n'.format(**geo))

    # painting vertical lines
    for step in range(x_amount + 1):
        if step:
            geo = {
                    'x': x_step * step + x_step / 2,
                    'y': y_step - (box_size - font_size) / 2,
                    'data': step - 1,
                    }

            out.write('<text style="fill: gray;" x="{x}" y="{y}">{data}</text>\n'.format(**geo))

        geo = {
                'y_size': size[1],
                'x': x_step * step,
                }

        out.write('<line y1="0" y2="{y_size}" x1="{x}" x2="{x}" />\n'.format(**geo))

    # painting the data
    for (x, y), value in data:
        geo =  {
            'pos_x': x_step * (x + 1) + x_step / 2,
            'pos_y': y_step * (y + 1) + y_step / 2,
            'size': size_step * value,
        }

        out.write('<circle cx="{pos_x}" cy="{pos_y}" r="{size}"/>\n'.format(**geo))

    out.write('</g>')
    out.write('</svg>\n')

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

