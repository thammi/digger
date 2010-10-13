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

class Element:

    def __init__(self, tag, paras=None):
        # wth?
        if paras == None:
            paras = {}

        self.tag = tag
        self._paras = paras
        self._style = {}

    def translate(self, (delta)):
        # TODO: replaces other transformations!
        self._paras['transform'] = "translate({x} {y})".format(x=delta[0], y=delta[1])

    def style(self, key, value):
        self._style[key] = value

    def write(self, out):
        out.write("<{0}".format(self.tag))

        # getting style
        style = self._style
        if style:
            out.write(' style="')
            for key, value in style.iteritems():
                out.write("{key}: {value}; ".format(key=key, value=value))
            out.write('"')
        
        # explicit parameters
        for key, value in self._paras.iteritems():
            out.write(' {key}="{value}"'.format(key=key, value=value))

        if hasattr(self, 'payload'):
            out.write(">\n")
            self.payload(out)
            out.write("</{0}>\n".format(self.tag))
        else:
            out.write(" />\n")

class Text(Element):
    def __init__(self, text, position):
        self.text = text

        paras = {
                'x': position[0],
                'y': position[1],
                }

        Element.__init__(self, 'text', paras)

    def payload(self, out):
        out.write(self.text)

class Circle(Element):

    def __init__(self, radius, position):
        paras = {
                'cx': position[0],
                'cy': position[1],
                'r': radius,
                }

        Element.__init__(self, 'circle', paras)

class Line(Element):

    def __init__(self, start, to):
        paras = {
                'x1': start[0],
                'y1': start[1],
                'x2': to[0],
                'y2': to[1],
                }

        Element.__init__(self, 'line', paras)

class Group(Element):

    def __init__(self):
        Element.__init__(self, "g")
        self.subs = []

    def add(self, element):
        self.subs.append(element)

    def payload(self, out):
        for sub in self.subs:
            sub.write(out)

class SVG(Group):

    def __init__(self, size):
        self.size = size

        Group.__init__(self)

    def write(self, out):
        # header
        out.write('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN" "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd">')
        out.write('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="%ipx" height="%ipx">\n' % self.size)

        # background
        out.write('<rect x="0" y="0" width="%i" height="%i" fill="white" />' % self.size)

        # root group
        Element.write(self, out)

        # footer
        out.write('</svg>')

