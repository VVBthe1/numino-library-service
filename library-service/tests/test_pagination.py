from app.rpc.pagination import next_page_token, resolve_page


def test_resolve_page_defaults():
    assert resolve_page(0, "") == (20, 0)


def test_resolve_page_token_and_cap():
    assert resolve_page(200, "40") == (100, 40)


def test_resolve_page_rejects_bad_token():
    try:
        resolve_page(10, "abc")
        assert False
    except ValueError as exc:
        assert "page_token" in str(exc)


def test_next_page_token():
    rows = [1, 2, 3, 4]
    page, token = next_page_token(0, 3, rows)
    assert page == [1, 2, 3]
    assert token == "3"
    page2, token2 = next_page_token(3, 3, [4])
    assert page2 == [4]
    assert token2 == ""
