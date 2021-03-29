import urwid

from ip_object_browser import browse


class FlagFileWidget(urwid.TreeWidget):
    # apply an attribute to the expand/unexpand icons
    unexpanded_icon = urwid.AttrMap(urwid.TreeWidget.unexpanded_icon, "dirmark")
    expanded_icon = urwid.AttrMap(urwid.TreeWidget.expanded_icon, "dirmark")

    def render(self, size, focus=False):
        if focus:
            render_footer(self.browser, self._node.get_value())
        return super().render(size, focus=focus)

    def __init__(self, browser, node):
        assert isinstance(browser, browse.DirectoryBrowser)
        self.__super.__init__(node)
        self.browser = browser
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
            self.expanded = False
        elif key == "l":
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

    def __init__(self, browser, node):
        assert isinstance(browser, browse.DirectoryBrowser)
        self.__super.__init__(browser, node)
        self.expanded = False
        self.update_expanded_icon()

    def get_display_text(self):
        node = self.get_node()
        return str(get_display(node.path))


def items(x):
    if isinstance(x, dict):
        return x.items()
    return enumerate(x)


def render_path(path):
    if path and path[-1] == -1:
        path = path[:-1]
    return "".join(f"[{x!r}]" for x in path)


def render_footer(browser, new_path):
    browser.footer.set_edit_text(render_path(new_path))


def get_display(key):
    try:
        return key[-1]
    except IndexError:
        return "."
