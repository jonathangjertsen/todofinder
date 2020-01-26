from typing import Callable, Optional, List

import todofinder
from todofinder import TodoContext, Todo, scan_line

_plugins = {}
_enabled_plugins = {}
_scan_line_original = scan_line
_plugin_state = {
    "python_in_multiline_comment": False,
    "python_last_file": None,
    "c_in_multiline_comment": False,
    "c_last_file": None,
}

ScanLineFunction = Callable[[str, TodoContext], Optional[Todo]]

def plugin_names() -> List[str]:
    return list(_plugins) + ["all"]

def plugin(filetype: str) -> Callable[[ScanLineFunction], ScanLineFunction]:
    def decorator(func: ScanLineFunction) -> ScanLineFunction:
        _plugins[filetype] = func
        return func
    return decorator

def scan_line_with_plugins(line: str, context: TodoContext) -> Optional[Todo]:
    for filetype, func in _enabled_plugins.items():
        if filetype == context.filetype:
            return func(line, context)
    else:
        return _scan_line_original(line, context)

def swap_scan_line_function(filetypes):
    global _enabled_plugins
    _enabled_plugins = { key: value for key, value in _plugins.items() if key in filetypes }
    todofinder.scan_line = scan_line_with_plugins

def restore_scan_line_function():
    todofinder.scan_line = _scan_line_original

@plugin("py")
def py(line: str, context: TodoContext) -> Optional[Todo]:
    """
    Line scanner that takes multi-line comments into account
    """
    # Restart state when there is a new file
    if _plugin_state["python_last_file"] != context.file:
        _plugin_state["python_in_multiline_comment"] = False
        _plugin_state["python_last_file"] = context.file

    # Figure out if we are in a multiline comment and keep the global state in sync
    in_multiline_comment = _plugin_state["python_in_multiline_comment"]
    n_multiline_tokens = line.count('"""')
    if n_multiline_tokens & 1:
        in_multiline_comment = not in_multiline_comment
        _plugin_state["python_in_multiline_comment"] = in_multiline_comment

    # Figure out if we have a comment, and pick out the relevant part if necessary
    has_comment = in_multiline_comment
    if "#" in line:
        line = "".join(line.split("#")[1:])
        has_comment = True
    if '"""' in line:
        line = "".join(line.split('"""')[1:])
        has_comment = True

    # Only scan if there is a comment in there
    if has_comment:
        return _scan_line_original(line, context)
    else:
        return None

@plugin("c")
def c(line: str, context: TodoContext) -> Optional[Todo]:
    # Restart state when there is a new file
    if _plugin_state["c_last_file"] != context.file:
        _plugin_state["c_in_multiline_comment"] = False
        _plugin_state["c_last_file"] = context.file

    # Figure out if we are in a multiline comment and keep the global state in sync
    in_multiline_comment = _plugin_state["c_in_multiline_comment"]
    n_multiline_tokens = line.count('/*') + line.count('*/')
    if n_multiline_tokens & 1:
        in_multiline_comment = not in_multiline_comment
        _plugin_state["c_in_multiline_comment"] = in_multiline_comment

    # Figure out if we have a comment, and pick out the relevant part if necessary
    has_comment = in_multiline_comment
    if "//" in line:
        line = "".join(line.split("//")[1:])
        has_comment = True
    if '/*' in line:
        if '*/' in line:
            line = "".join(line.split('/*')[1:]).split('*/')[0]
        else:
            line = "".join(line.split('/*')[1:])
        has_comment = True

    # Only scan if there is a comment in there
    if has_comment:
        return _scan_line_original(line, context)
    else:
        return None
