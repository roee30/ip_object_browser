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

import itertools
import re
from boltons.iterutils import is_collection

import urwid


class FlagFileWidget(urwid.TreeWidget):
    # apply an attribute to the expand/unexpand icons
    unexpanded_icon = urwid.AttrMap(urwid.TreeWidget.unexpanded_icon, "dirmark")
    expanded_icon = urwid.AttrMap(urwid.TreeWidget.expanded_icon, "dirmark")

    def __init__(self, node):
        self.__super.__init__(node)
        # insert an extra AttrWrap for our own use
        self._w = urwid.AttrWrap(self._w, None)
        self.flagged = False
        self.update_w()

    def selectable(self):
        return True

    def keypress(self, size, key):
        """allow subclasses to intercept keystrokes"""
        key = self.__super.keypress(size, key)
        if key:
            key = self.unhandled_keys(size, key)
        return key

    def unhandled_keys(self, size, key):
        """
        Override this method to intercept keystrokes in subclasses.
        Default behavior: Toggle flagged on space, ignore other keys.
        """
        if key in ("left", "h"):
            #  self.flagged = not self.flagged
            self.expanded = False
        elif key == "l":
            #  self.flagged = not self.flagged
            self.expanded = True
        else:
            return key
        self.update_w()
        return key

    def update_w(self):
        """Update the attributes of self.widget based on self.flagged."""
        if self.flagged:
            self._w.attr = "flagged"
            self._w.focus_attr = "flagged focus"
        else:
            self._w.attr = "body"
            self._w.focus_attr = "focus"


class FileTreeWidget(FlagFileWidget):
    """Widget for individual files."""

    def __init__(self, node):
        self.__super.__init__(node)
        path = node.get_value()
        add_widget(path, self)

    def get_display_text(self):
        return get_display(self.get_node().path)


class TextWidget(FileTreeWidget):
    def get_display_text(self):
        return repr(self.get_node().text)


class EmptyWidget(urwid.TreeWidget):
    """A marker for expanded directories with no contents."""

    def get_display_text(self):
        return ("flag", "(empty directory)")


class ErrorWidget(urwid.TreeWidget):
    """A marker for errors reading directories."""

    def get_display_text(self):
        return ("error", "(error/permission denied)")


class DirectoryWidget(FlagFileWidget):
    """Widget for a directory."""

    def __init__(self, node):
        self.__super.__init__(node)
        path = node.get_value()
        add_widget(path, self)
        #  self.expanded = starts_expanded(path)
        self.expanded = False
        self.update_expanded_icon()

    def get_display_text(self):
        node = self.get_node()
        return str(get_display(node.path))


def get_display(key):
    try:
        return key[-1]
    except IndexError:
        return "."


class FileNode(urwid.TreeNode):
    """Metadata storage for individual files"""

    def __init__(self, path, parent=None):
        depth = len(path)
        key = path
        self.path = path

        super().__init__(path, key=key[-1], parent=parent, depth=depth)

    @property
    def parent_path(self):
        return self.path[:-1]

    def load_parent(self):
        raise NotImplementedError()

    def load_widget(self):
        1 / 0
        return FileTreeWidget(self)


class TextNode(FileNode):
    def __init__(self, text, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = text

    def load_widget(self):
        return TextWidget(self)


class EmptyNode(urwid.TreeNode):
    def load_widget(self):
        return EmptyWidget(self)


class ErrorNode(urwid.TreeNode):
    def load_widget(self):
        return ErrorWidget(self)


def items(x):
    if isinstance(x, dict):
        return x.items()
    return enumerate(x)


FIRST_KEY = ()


class DirectoryNode(urwid.ParentNode):
    """Metadata storage for directories"""

    def __init__(self, path, obj, parent=None):
        self.obj = obj
        self.path = path
        if path:
            depth = len(path)
            key = path[-1]
        else:
            depth = 0
            key = None
            #  key = path[:-1]
            #  key = path[:-1]
        super().__init__(path, key=key, parent=parent, depth=depth)

    def load_parent(self):
        raise NotImplementedError()

    def load_child_keys(self):
        dirs = []
        files = []
        try:
            # separate dirs and files
            for key, value in items(self.obj):
                if is_collection(value):
                    dirs.append((key, value))
                else:
                    files.append((key, value))
        except OSError as e:
            depth = self.get_depth() + 1
            self._children[None] = ErrorNode(self, parent=self, key=None, depth=depth)
            return [None]

        # sort dirs and files
        #  dirs.sort()
        #  files.sort()
        # store where the first file starts
        self.dir_count = len(dirs)
        # collect dirs and files together again
        keys = [key for key, _ in dirs + files]
        if len(keys) == 0:
            depth = self.get_depth() + 1
            self._children[None] = EmptyNode(self, parent=self, key=None, depth=depth)
            keys = [None]
        return keys

    def load_child_node(self, key):
        """Return either a FileNode or DirectoryNode"""
        index = self.get_child_index(key)
        if key is None:
            return EmptyNode(None)
        else:
            new_key = (*self.path, key)
            if index < self.dir_count:
                result = DirectoryNode(new_key, self.obj[key], parent=self)
            else:
                result = ScalarNode(self.obj[key], new_key, self.obj[key], parent=self)
                #  result= FileNode(new_key, parent=self)
            return result

    def load_widget(self):
        return DirectoryWidget(self)

    #  def get_child_index(self, key):
    #  return self.load_child_keys().index(key)


class ScalarNode(DirectoryNode):
    def __init__(self, text, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = text

    def load_child_keys(self):
        return [0]

    def load_child_node(self, key):
        index = self.get_child_index(key)
        if key is None:
            return EmptyNode(None)
        else:
            new_key = (*self.path, key)
            if False and index < self.dir_count:
                value = self.obj[key]
                result = DirectoryNode(new_key, value, parent=self)
            else:
                value = self.obj
                result = TextNode(self.obj, new_key, parent=self)
            return result


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
        self.header = urwid.Text("")
        self.listbox = urwid.TreeListBox(
            urwid.TreeWalker(DirectoryNode(FIRST_KEY, obj))
        )
        self.listbox._command_map._command.update({
            'h': 'cursor left',
            'j': 'cursor down',
            'k': 'cursor up',
            'l': 'cursor right',
            })
        urwid.TreeListBox(urwid.TreeWalker(DirectoryNode(FIRST_KEY, obj)))
        self.listbox.offset_rows = 1
        self.footer = urwid.AttrWrap(urwid.Text(self.footer_text), "foot")
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
        names = [escape_filename_sh(x) for x in get_flagged_names()]
        print(" ".join(names))

    def unhandled_input(self, k):
        # update display of focus directory
        if k in ("q", "Q"):
            raise urwid.ExitMainLoop()


def view(obj):
    try:
        DirectoryBrowser(obj).main()
    except KeyboardInterrupt:
        pass


#######
# global cache of widgets
_widget_cache = {}


def add_widget(path, widget):
    """Add the widget for a given path"""

    _widget_cache[path] = widget


def get_flagged_names():
    """Return a list of all filenames marked as flagged."""

    l = []
    for w in _widget_cache.values():
        if w.flagged:
            l.append(w.get_node().get_value())
    return l


######
# store path components of initial current working directory


def escape_filename_sh(name):
    """Return a hopefully safe shell-escaped version of a filename."""

    # check whether we have unprintable characters
    for ch in name:
        if ord(ch) < 32:
            # found one so use the ansi-c escaping
            return escape_filename_sh_ansic(name)

    # all printable characters, so return a double-quoted version
    name.replace("\\", "\\\\")
    name.replace('"', '\\"')
    name.replace("`", "\\`")
    name.replace("$", "\\$")
    return '"' + name + '"'


def escape_filename_sh_ansic(name):
    """Return an ansi-c shell-escaped version of a filename."""

    out = []
    # gather the escaped characters into a list
    for ch in name:
        if ord(ch) < 32:
            out.append("\\x%02x" % ord(ch))
        elif ch == "\\":
            out.append("\\\\")
        else:
            out.append(ch)

    # slap them back together in an ansi-c quote  $'...'
    return "$'" + "".join(out) + "'"


#  if __name__=="__main__":
#  main()
