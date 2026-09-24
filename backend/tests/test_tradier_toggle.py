import pytest
import os
import sys
import importlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

def test_dry_run_uses_mock():
    os.environ["DRY_RUN"] = "true"
    import tradier_client
    importlib.reload(tradier_client)
    data = tradier_client.get_chain("SPX")
    assert data["source"] == "mock"
    assert data["ticker"] == "SPX"
    assert len(data["strikes"]) > 0
    assert not tradier_client.is_fake_chain(data)

def test_junk_rejected_even_in_dry_run():
    os.environ["DRY_RUN"] = "true"
    import tradier_client
    importlib.reload(tradier_client)
    with pytest.raises(ValueError):
        tradier_client.get_chain("JUNK123")

def test_empty_token_fallback_to_mock():
    os.environ["DRY_RUN"] = "false"
    os.environ["TRADIER_TOKEN"] = ""
    import tradier_client
    importlib.reload(tradier_client)
    data = tradier_client.get_chain("AAPL")
    assert data["source"] == "mock"
    assert not tradier_client.is_fake_chain(data)

def test_market_closed_fallback():
    os.environ["DRY_RUN"] = "false"
    os.environ["TRADIER_TOKEN"] = "fake_token"
    import tradier_client
    importlib.reload(tradier_client)
    data = tradier_client.get_chain("SPY")
    assert data["source"] == "mock"
    assert len(data["strikes"]) == 21

def test_spx_never_undefined_with_toggle():
    os.environ["DRY_RUN"] = "true"
    import tradier_client
    importlib.reload(tradier_client)
    for ticker in ["SPX", "SPY", "QQQ"]:
        data = tradier_client.get_chain(ticker)
        for s in data["strikes"]:
            assert "undefined" not in str(s["bid"]).lower()
            assert float(s["mid"]) > 0

def test_width_calc_still_works_with_toggle():
    os.environ["DRY_RUN"] = "true"
    import tradier_client
    importlib.reload(tradier_client)
    data = tradier_client.get_chain("SPX")
    short_strike = data["strikes"][10]["strike"]
    long_strike = data["strikes"][12]["strike"]
    width = abs(long_strike - short_strike)
    assert width == 10
