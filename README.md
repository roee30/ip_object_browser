# ip_object_browser
Using IPython? Did a REST endpoint return 5 MB of JSON data? Can't bother to save the response to a file?
Browse it with your keyboard straight from the console!

## Usage

In IPython, press `<C-T>` to browse the last output object (`_`).

Use vi-like `hjkl` or arrow keys to navigate. 

Press `/` to begin a textual search.
Confirm with enter.
Jump to next occurrence with `n`.

Press `<C-C>` or `q` to exit.

### Usage from code
```python
from ip_object_browser import view
view({})
```

## Installation
```bash
pip install ip-object-browser
cat <<EOF >>~/.ipython/profile_default/ipython_config.py
c = get_config()
c.InteractiveShellApp.exec_lines.append(
    "try:\n    %load_ext ip_object_browser\nexcept ImportError: pass"
)
EOF
```

## Implementation
Based on the [urwid](https://github.com/urwid/urwid) library,
adapted from the [treesample example](https://github.com/urwid/urwid/blob/master/examples/treesample.py).

## TODO
- [x] textual search functionality
    - [ ] fix jump to previous (`N`)
- [x] status line with current path in object
- [ ] path-based navigation
- [x] output current path on exit
