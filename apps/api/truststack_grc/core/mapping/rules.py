from __future__ import annotations

from dataclasses import dataclass
from typing import Any

ROOT_KEYS = {"industry", "segment", "use_case", "tags", "pattern", "data", "deployment", "jurisdiction", "model", "system"}

@dataclass
class Trace:
    matched: list[str]

def get_path(obj: dict[str, Any], path: str) -> Any:
    cur: Any = obj
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur

def is_path_token(x: Any) -> bool:
    if not isinstance(x, str):
        return False
    if "." in x:
        return True
    return x in ROOT_KEYS

def resolve_operand(context: dict[str, Any], operand: Any) -> Any:
    if is_path_token(operand):
        return get_path(context, operand)
    return operand

def eval_rule(rule: dict[str, Any] | None, context: dict[str, Any]) -> tuple[bool, Trace]:
    if not rule:
        return True, Trace(matched=["(no applicability rule)"])
    if len(rule) != 1:
        raise ValueError(f"Rule must have exactly one operator, got: {list(rule.keys())}")

    op, arg = next(iter(rule.items()))

    if op == "all":
        matched: list[str] = []
        for sub in arg or []:
            ok, tr = eval_rule(sub, context)
            if not ok:
                return False, Trace(matched=matched)
            matched.extend(tr.matched)
        return True, Trace(matched=matched)

    if op == "any":
        any_matched: list[str] = []
        for sub in arg or []:
            ok, tr = eval_rule(sub, context)
            if ok:
                any_matched.extend(tr.matched)
                return True, Trace(matched=any_matched)
        return False, Trace(matched=[])

    if op == "not":
        ok, tr = eval_rule(arg, context)
        return (not ok), Trace(matched=[] if ok else tr.matched)

    if op == "equals":
        a, b = arg
        va = resolve_operand(context, a)
        vb = resolve_operand(context, b)
        ok = va == vb
        return ok, Trace(matched=[f"{a} == {b} (resolved {va!r} == {vb!r})"] if ok else [])

    if op == "in":
        needle, haystack = arg
        vneedle = resolve_operand(context, needle)
        vhay = resolve_operand(context, haystack)
        ok = False
        if isinstance(vhay, (list, tuple, set)):
            ok = vneedle in vhay
        elif isinstance(vhay, str):
            ok = str(vneedle) in vhay
        return ok, Trace(matched=[f"{needle} in {haystack} (resolved {vneedle!r} in {vhay!r})"] if ok else [])

    if op == "exists":
        path = arg
        v = get_path(context, path) if isinstance(path, str) else None
        ok = v is not None
        return ok, Trace(matched=[f"exists({path})"] if ok else [])

    if op == "contains":
        container, item = arg
        vcontainer = resolve_operand(context, container)
        vitem = resolve_operand(context, item)
        ok = False
        if isinstance(vcontainer, (list, tuple, set)):
            ok = vitem in vcontainer
        elif isinstance(vcontainer, str):
            ok = str(vitem) in vcontainer
        return ok, Trace(matched=[f"{container} contains {item}"] if ok else [])

    if op == "has_tag":
        tag = arg
        tags = context.get("tags", [])
        ok = tag in tags
        return ok, Trace(matched=[f"has_tag({tag})"] if ok else [])

    raise ValueError(f"Unknown operator: {op}")
