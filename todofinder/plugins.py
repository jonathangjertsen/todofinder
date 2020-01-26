from typing import Optional

import todofinder
from todofinder import TodoContext, Todo, scan_line

_plugins = {}
_enabled_plugins = {}
_scan_line_original = scan_line

def plugin_names():
    return list(_plugins)

def plugin(filetype):
    def wrapper2(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        _plugins[filetype] = wrapper
    return wrapper2

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
    return _scan_line_original(line, context)

@plugin("c")
def c(line: str, context: TodoContext) -> Optional[Todo]:
    return _scan_line_original(line, context)

@plugin("md")
def md(line: str, context: TodoContext) -> Optional[Todo]:
    return _scan_line_original(line, context)
