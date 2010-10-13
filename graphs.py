#!/usr/bin/env python
###############################################################################
##
## digger - Digging into some data mines
## Copyright (C) 2010  Thammi
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


import svg
from matplotlib.dates import date2num
import Image
from ImageDraw import Draw
from datetime import date, datetime

import matplotlib as mpl
mpl.use('Agg')
import pylab


def aggre_count(items, key=None):
    """Counting the occurences of aspects defined by a key"""
    counter = {}
    
    for item in items:
        if key:
            value = key(item)
        else:
            value = item

        if value in counter:
            counter[value] += 1
        else:
            counter[value] = 1

    return counter

def iter_months(start, end):
    for year in xrange(start.year, end.year + 1):
        start_month = start.month + 1 if start.year == year else 1

        for month in range(start_month, 12 + 1):
            if end.year == year and month > end.month:
                break

            yield datetime(year, month, 1)

def roll_date_time(data, out, hour_parts=4, lines=4):
    bg_color = (255, 255, 255)
    line_color = (220, 220, 220)
    color=(32,32,255)

    def date_value(event):
        return (event.date() - epoch).days

    def date_coords(event):
        time_value = event.hour * hour_parts + event.minute * hour_parts / 60
        return (date_value(event) - start_value, height - time_value - 1)

    epoch = date(1970, 1, 1)

    # find boundarys
    start = min(data)
    end = max(data)

    # calculate value of boundarys
    start_value = date_value(start)
    end_value = date_value(end)

    # calculate geometry
    width = end_value - start_value + 1
    height = 24 * hour_parts

    # building the image
    img = Image.new("RGB", (width, height + 10), bg_color)
    draw = Draw(img)

    # drawing horizontal (time) lines to enhance readability
    for line in xrange(lines):
        y = (height / lines) * (line + 1)
        draw.line([(0, y), (width - 1, y)], line_color)

    # drawing vertical (date) lines and captions
    for month_start in iter_months(start, end):
        x, _ = date_coords(month_start)
        draw.line([(x, 0), (x, height - 1)], line_color)
        draw.text((x + 3, height), month_start.strftime("%m"), line_color)

    # plotting actual data
    for event in data:
        img.putpixel(date_coords(event), color)

    img.save(out, 'png')

def line_plot(data, out):
    """Turning ([key, ...], [value, ...]) into line graphs"""
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

