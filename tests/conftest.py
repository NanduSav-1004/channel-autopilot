import urllib.request

import pytest


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """Tests must never touch the network. Code that fails soft (demand scoring) just sees an outage;
    tests that need a response install their own urlopen, which overrides this."""
    def blocked(*args, **kwargs):
        raise OSError("network access is disabled in tests")

    monkeypatch.setattr(urllib.request, "urlopen", blocked)
