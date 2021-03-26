from IPython import get_ipython
from prompt_toolkit.enums import DEFAULT_BUFFER
from prompt_toolkit.keys import Keys
from prompt_toolkit.filters import HasFocus, HasSelection, ViInsertMode, EmacsInsertMode
from prompt_toolkit.key_binding.bindings.named_commands import get_by_name
from .browse import view


def load_ipython_extension(ip):

    insert_mode = ViInsertMode() | EmacsInsertMode()


    def insert_unexpected(event):
        #  buf = event.current_buffer
        #  buf.insert_text("view(_)")
        #  get_by_name('accept-line').handler(event)
        view(ip.user_ns['_'])


    # Register the shortcut if IPython is using prompt_toolkit
    if getattr(ip, "pt_app", None):
        registry = ip.pt_app.key_bindings
        registry.add_binding(
            Keys.ControlT, filter=(HasFocus(DEFAULT_BUFFER) & ~HasSelection() & insert_mode)
        )(insert_unexpected)
