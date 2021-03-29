#!/usr/bin/env python
#
# Urwid example lazy directory browser / tree view
#    Copyright (C) 2004-2011  Ian Ward
#    Copyright (C) 2010  Kirk McDonald
#    Copyright (C) 2010  Rob Lanphier
#    Copyright (C) 2021  Roee Nizan
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Urwid web site: http://excess.org/urwid/

"""
Urwid example lazy directory browser / tree view

Features:
- custom selectable widgets for files and directories
- custom message widgets to identify access errors and empty directories
- custom list walker for displaying widgets in a tree fashion
- outputs a quoted list of files and directories "selected" on exit
"""

from __future__ import print_function

import urwid

from ip_object_browser.nodes import DirectoryNode
from ip_object_browser.search import search

FIRST_KEY = ()


class DirectoryBrowser:
    palette = [
        ("body", "black", "light gray"),
        ("flagged", "black", "dark green", ("bold", "underline")),
        ("focus", "light gray", "dark blue", "standout"),
        ("flagged focus", "yellow", "dark cyan", ("bold", "standout", "underline")),
        ("head", "yellow", "black", "standout"),
        ("foot", "light gray", "black"),
        ("key", "light cyan", "black", "underline"),
        ("title", "white", "black", "bold"),
        ("dirmark", "black", "dark cyan", "bold"),
        ("flag", "dark gray", "light gray"),
        ("error", "dark red", "light gray"),
    ]

    footer_text = [
        ("title", "Directory Browser"),
        "    ",
        ("key", "UP"),
        ",",
        ("key", "DOWN"),
        ",",
        ("key", "PAGE UP"),
        ",",
        ("key", "PAGE DOWN"),
        "  ",
        ("key", "SPACE"),
        "  ",
        ("key", "+"),
        ",",
        ("key", "-"),
        "  ",
        ("key", "LEFT"),
        "  ",
        ("key", "HOME"),
        "  ",
        ("key", "END"),
        "  ",
        ("key", "Q"),
    ]

    def __init__(self, obj):
        self.obj = obj
        self.root_node = DirectoryNode(self, FIRST_KEY, obj)
        self.header = urwid.Text("")
        self.listbox = urwid.TreeListBox(urwid.TreeWalker(self.root_node))
        self.listbox._command_map._command.update(
            {
                "h": "cursor left",
                "j": "cursor down",
                "k": "cursor up",
                "l": "cursor right",
            }
        )
        self.listbox.offset_rows = 1
        self.footer = SEdit(self, "")
        self.view = urwid.Frame(
            urwid.AttrWrap(self.listbox, "body"),
            header=urwid.AttrWrap(self.header, "head"),
            footer=self.footer,
        )

    def main(self):
        """Run the program."""

        self.loop = urwid.MainLoop(
            self.view, self.palette, unhandled_input=self.unhandled_input
        )
        self.loop.run()

        # on exit, write the flagged filenames to the console
        print(self.footer.edit_text)

    def unhandled_input(self, k):
        # update display of focus directory
        if k in ("q", "Q"):
            raise urwid.ExitMainLoop()
        elif k == "/":
            self.footer.start()
        elif k == "n":
            self.footer.next()
        elif k == "N":
            self.footer.previous()


class SEdit(urwid.Edit):
    def __init__(self, browser, *args, **kwargs):
        self.browser = browser
        self._cache = None
        super().__init__(*args, **kwargs)

    def keypress(self, size, key):
        if key == "enter":
            self.end()
        return super().keypress(size, key)

    def start(self):
        self.set_edit_text("")
        self.browser.view.focus_position = "footer"

    def end(self):
        self._cache = self.edit_text
        self.next()
        self.browser.view.focus_position = "body"

    def next(self):
        search(self.browser, self.browser.listbox._body, self._cache)

    def previous(self):
        search(self.browser, self.browser.listbox._body, self._cache, reverse=True)


def view(obj):
    try:
        DirectoryBrowser(obj).main()
    except KeyboardInterrupt:
        pass
