#!/usr/bin/env python

import svg
from matplotlib.dates import date2num

def aggre_count(commits, key):
    """Counting the occurences of aspects defined by a key"""
    counter = {}
    
    for commit in commits:
        value = key(commit)
        if value in counter:
            counter[value] += 1
        else:
            counter[value] = 1

    return counter

def line_plot(data, out):
    """Turning ([key, ...], [value, ...]) into line graphs"""
    import matplotlib as mpl
    mpl.use('Agg')
    import pylab

    pylab.clf()

    pylab.plot_date(data[0], data[1], '-')

    pylab.savefig(out)

def punch_svg(data, out, size = (800, 300)):
    """Turning [((x, y), value), ...] into punchcards"""

    max_point = max(value for key, value in data)
    x_amount = max(x for (x, y), value in data) + 1
    y_amount = max(y for (x, y), value in data) + 1

    x_step = float(size[0]) / (x_amount + 1)
    y_step = float(size[1]) / (y_amount + 1)
    box_size = min(float(size[0])/x_amount, float(size[1])/y_amount)
    size_step = box_size / 2 * 0.8 / max_point
    font_size = box_size*0.7
    
    # root of the svg image
    root = svg.SVG(size)
    root.style('fill', 'black')
    root.style('stroke', 'grey')

    # group transformed into the area containing the data
    card = svg.Group()
    root.add(card)
    card.translate((x_step, y_step))

    # group containing the captions (relative to card)
    caption = svg.Group()
    card.add(caption)
    caption.style('fill', 'grey')
    caption.style('font-size', font_size)
    caption.style('text-anchor', 'middle')

    # vertical captions
    for step in range(y_amount):
        y = y_step * (step + 1) - (box_size - font_size) / 2
        x = - x_step / 2

        caption.add(svg.Text(str(step), (x, y)))

    # horizontal captions
    for step in range(x_amount):
        x = x_step * step + x_step / 2
        y = -(box_size - font_size) / 2

        caption.add(svg.Text(str(step), (x, y)))

    # painting horizontal lines
    for step in range(y_amount + 2):
        y = y_step * step
        root.add(svg.Line((0, y), (size[0], y)))

    # painting vertical lines
    for step in range(x_amount + 2):
        x = x_step * step
        root.add(svg.Line((x, 0), (x, size[1])))

    # painting the data
    for (x, y), value in data:
        x = x_step * x + x_step / 2
        y = y_step * y + y_step / 2
        radius = size_step * value

        card.add(svg.Circle(radius, (x, y)))

    root.write(out)

def _paint_curve(agg):
    keys = agg.keys()
    keys.sort()

    values = [agg[key] for key in keys]

    data = (keys, values)
    #data = values

    f = file("out.png", "w")
    line_plot(data, f)
    f.close()

def _paint_punchcard(commits):
    agg = aggre_count(commits, lambda c: (c['date'][3], date_to_weekday(c['date'])))

    keys = agg.keys()
    data = [(key, agg[key]) for key in keys]

    f = file("out.svg", 'w')
    punch_svg(data, f)
    f.close()

def _main(argv):
    from git_stats import Base, date_to_weekday
    from matplotlib.dates import date2num
    from datetime import datetime

    b = Base()

    data = b.commits()
    #data = b.groups[25].commits()

    agg = aggre_count(data, lambda c: date2num(datetime(*c['date'][:3])))
    _paint_curve(agg)

if __name__ == '__main__':
    import sys
    _main(sys.argv[1:])

