from truststack_grc.core.mapping.rules import eval_rule

def test_rules_equals_and_any():
    ctx = {"tags": ["llm"], "data": {"phi": True}, "jurisdiction": {"list": ["US"]}}
    ok, _ = eval_rule({"any": [{"has_tag": "llm"}, {"equals": ["data.phi", False]}]}, ctx)
    assert ok

def test_rules_in():
    ctx = {"jurisdiction": {"list": ["EU", "US"]}}
    ok, _ = eval_rule({"in": ["EU", "jurisdiction.list"]}, ctx)
    assert ok
