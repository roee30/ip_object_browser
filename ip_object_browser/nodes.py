import urwid
from boltons.iterutils import is_collection

from . import browse
from .widgets import (
    FileTreeWidget,
    TextWidget,
    EmptyWidget,
    ErrorWidget,
    DirectoryWidget,
    items,
)


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
    def __init__(self, browser, text, *args, **kwargs):
        assert isinstance(browser, browse.DirectoryBrowser)
        super().__init__(*args, **kwargs)
        self.browser = browser
        self.text = text

    def load_widget(self):
        return TextWidget(self.browser, self)


class EmptyNode(urwid.TreeNode):
    def load_widget(self):
        return EmptyWidget(self)


class ErrorNode(urwid.TreeNode):
    def load_widget(self):
        return ErrorWidget(self)


class DirectoryNode(urwid.ParentNode):
    """Metadata storage for directories"""

    def __init__(self, browser, path, obj, parent=None):
        assert isinstance(browser, browse.DirectoryBrowser)
        self.browser = browser
        self.obj = obj
        self.path = path
        if path:
            depth = len(path)
            key = path[-1]
        else:
            depth = 0
            key = None
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

        # store where the first file starts
        self.dir_count = len(dirs)
        # collect dirs and files together again
        keys = [key for key, _ in dirs + files]
        if not keys:
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
                result = DirectoryNode(
                    self.browser, new_key, self.obj[key], parent=self
                )
            else:
                result = ScalarNode(
                    self.browser, self.obj[key], new_key, self.obj[key], parent=self
                )
            return result

    def load_widget(self):
        return DirectoryWidget(self.browser, self)


class ScalarNode(DirectoryNode):
    def __init__(self, browser, text, *args, **kwargs):
        super().__init__(browser, *args, **kwargs)
        self.text = text

    def load_child_keys(self):
        return [-1]

    def load_child_node(self, key):
        if key is None:
            return EmptyNode(None)
        else:
            new_key = (*self.path, key)
            return TextNode(self.browser, self.obj, new_key, parent=self)
