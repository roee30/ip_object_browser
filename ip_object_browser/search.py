from itertools import chain
from .nodes import TextNode, EmptyNode


def walk_children(node):
    if isinstance(node, TextNode):
        yield node, node.text
    elif isinstance(node, EmptyNode):
        return
    else:
        for key in node.get_child_keys():
            next_node = node.get_child_node(key)
            yield next_node, key
            yield from walk_children(next_node)


def walk(node):
    while node:
        parent = node.get_parent()
        if parent:
            keys = parent.get_child_keys()
            index = keys.index(node.get_value()[-1])
            for key in keys[index + 1 :]:
                next_node = parent.get_child_node(key)
                yield next_node, key
                yield from walk_children(next_node)
        node = parent


def _search(original_start, start, text, reverse=False):
    for node, t in direction(chain(walk_children(start), walk(start)), reverse=reverse):
        if node is original_start:
            break
        if text in str(t):
            return node
    return None


def search(browser, walker, text, reverse=False):
    start = walker.get_focus()[-1]

    if reverse:
        result = _search(start, browser.root_node, text, reverse=reverse) or _search(
            start, start, text, reverse=reverse
        )
    else:
        result = _search(start, start, text, reverse=reverse) or _search(
            start, browser.root_node, text, reverse=reverse
        )
    if result:
        walker.set_focus(result)


def direction(it, reverse=False):
    if reverse:
        x = reversed(list(it))
    return it
