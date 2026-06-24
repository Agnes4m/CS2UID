"""safe_log.py 单元测试。"""

from CS2UID.utils.api.safe_log import safe_log_response


def test_redact_token_top_level():
    raw = '{"access_token": "abcd1234", "name": "alice"}'
    out = safe_log_response(raw)
    assert "abcd1234" not in out
    assert "REDACTED" in out
    assert "alice" in out


def test_redact_token_nested():
    raw = '{"result": {"data": {"accessToken": "secret-XYZ"}}}'
    out = safe_log_response(raw)
    assert "secret-XYZ" not in out
    assert "REDACTED" in out


def test_redact_in_list():
    raw = '{"items": [{"token": "t1"}, {"token": "t2"}]}'
    out = safe_log_response(raw)
    assert "t1" not in out
    assert "t2" not in out


def test_redact_authorization_header():
    raw = '{"headers": {"Authorization": "Bearer abc.def.ghi"}}'
    out = safe_log_response(raw)
    assert "abc.def.ghi" not in out
    assert "REDACTED" in out


def test_passthrough_non_sensitive():
    raw = '{"steamId": "76561198", "level": 42}'
    out = safe_log_response(raw)
    assert "76561198" in out
    assert "42" in out


def test_invalid_json_kept_as_text():
    raw = "<html>not json</html>"
    out = safe_log_response(raw)
    assert out == "<html>not json</html>"


def test_truncation():
    raw = '{"data": "' + ("x" * 1000) + '"}'
    out = safe_log_response(raw, max_len=100)
    assert len(out) <= 120
    assert "truncated" in out


def test_empty_value_preserved():
    raw = '{"token": ""}'
    out = safe_log_response(raw)
    assert '"token": ""' in out
