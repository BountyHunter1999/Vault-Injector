from vault_injector.sources.base import JsonSource


def test_json_source():
    source = JsonSource()
    assert source.get_data() == []
    assert source.get_data_by_id("1") == {}
    assert source.put_data({}, None) == {}
