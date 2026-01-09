#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import types

# Shim for the 'imp' module which was removed in Python 3.12 but is required by 'crudbuilder'
if sys.version_info >= (3, 12):
    import importlib.util
    
    imp = types.ModuleType('imp')
    sys.modules['imp'] = imp
    
    def find_module(name, path=None):
        if path is None:
            path = sys.path
        for p in path:
            target = os.path.join(p, name + '.py')
            if os.path.exists(target):
                return (open(target), target, ('.py', 'r', 1)) # 1 = PY_SOURCE
            target_pkg = os.path.join(p, name)
            if os.path.isdir(target_pkg) and os.path.exists(os.path.join(target_pkg, '__init__.py')):
                return (None, target_pkg, ('', '', 5)) # 5 = PKG_DIRECTORY
        raise ImportError(f"No module named {name}")
    
    imp.find_module = find_module
    imp.load_module = lambda name, file, path, description: importlib.import_module(name)

def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
