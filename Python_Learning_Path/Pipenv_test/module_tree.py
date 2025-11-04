#!/usr/bin/env python3
from __future__ import annotations
import argparse
import importlib
import inspect
import pkgutil
from types import ModuleType
from typing import Any, Iterable, Tuple

TREE_BRANCH = "├── "
TREE_LAST   = "└── "
TREE_PIPE   = "│   "
TREE_SPACE  = "    "

def _is_private(name: str) -> bool:
    return name.startswith("_")

def _yield_members_sorted(module: ModuleType):
    classes, functions, others = [], [], []
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and getattr(obj, "__module__", "") == module.__name__:
            classes.append((name, obj))
        elif inspect.isfunction(obj) and getattr(obj, "__module__", "") == module.__name__:
            functions.append((name, obj))
        elif not (inspect.ismodule(obj) or inspect.isbuiltin(obj) or inspect.isroutine(obj) or inspect.isclass(obj)):
            others.append((name, obj))
    classes.sort(key=lambda x: x[0].lower())
    functions.sort(key=lambda x: x[0].lower())
    others.sort(key=lambda x: x[0].lower())
    return classes, functions, others

def _iter_submodules(module: ModuleType):
    if hasattr(module, "__path__"):
        for info in pkgutil.iter_modules(module.__path__):
            try:
                submod = importlib.import_module(f"{module.__name__}.{info.name}")
                yield info.name, submod
            except Exception:
                continue

def module_tree(module: ModuleType, max_depth: int = 2, include_private: bool = False, show_doc: bool = False):
    visited = set()

    def doc1(obj: Any) -> str:
        if not show_doc:
            return ""
        d = inspect.getdoc(obj) or ""
        first = d.strip().splitlines()[0] if d else ""
        return f" — {first}" if first else ""

    def walk_module(mod: ModuleType, prefix: str, depth: int):
        if id(mod) in visited:
            print(prefix + TREE_LAST + "(already visited)")
            return
        visited.add(id(mod))

        if depth > max_depth:
            return

        items = []

        if depth < max_depth:
            subs = list(_iter_submodules(mod)) or []
            subs.sort(key=lambda x: x[0].lower())
            for name, sm in subs:
                if not include_private and _is_private(name):
                    continue
                items.append(("submodule", name, sm))

        classes, functions, others = _yield_members_sorted(mod)

        for name, cls in classes:
            if not include_private and _is_private(name):
                continue
            items.append(("class", name, cls))
        for name, fn in functions:
            if not include_private and _is_private(name):
                continue
            items.append(("function", name, fn))
        for name, val in others:
            if not include_private and _is_private(name):
                continue
            preview = repr(val)
            if len(preview) > 60:
                preview = preview[:57] + "..."
            items.append(("const", f"{name} = {preview}", None))

        for i, (kind, name, obj) in enumerate(items):
            connector = TREE_LAST if i == len(items) - 1 else TREE_BRANCH
            line = f"{prefix}{connector}{name}"
            if kind in ("class", "function"):
                line += doc1(obj)
            print(line)

            if depth < max_depth:
                if kind == "class":
                    members = inspect.getmembers(obj)
                    own = []
                    for mname, mobj in members:
                        if not include_private and _is_private(mname):
                            continue
                        if inspect.isfunction(mobj) or inspect.ismethoddescriptor(mobj):
                            if mname in getattr(obj, "__dict__", {}):
                                own.append((mname, mobj))
                    own.sort(key=lambda x: x[0].lower())

                    for j, (mname, mobj) in enumerate(own):
                        sub_connector = TREE_LAST if j == len(own) - 1 else TREE_BRANCH
                        print(f"{prefix}{TREE_PIPE if i != len(items)-1 else TREE_SPACE}{sub_connector}{mname}" + (doc1(mobj)))

                elif kind == "submodule" and isinstance(obj, ModuleType):
                    walk_module(obj, prefix + (TREE_PIPE if i != len(items) - 1 else TREE_SPACE), depth + 1)

    walk_module(module, prefix="", depth=0)

def main():
    ap = argparse.ArgumentParser(description="Pretty tree view of a Python module.")
    ap.add_argument("module", help="Module name (e.g., 'datetime' or 'package.subpackage')")
    ap.add_argument("--depth", type=int, default=2, help="Max depth (default: 2)")
    ap.add_argument("--all", action="store_true", help="Include private names (starting with _)")
    ap.add_argument("--doc", action="store_true", help="Show first line of docstrings")
    args = ap.parse_args()

    mod = importlib.import_module(args.module)
    print(args.module)
    module_tree(mod, max_depth=args.depth, include_private=args.all, show_doc=args.doc)

if __name__ == "__main__":
    main()
