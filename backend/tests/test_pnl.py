import pytest
import sys
from pathlib import Path
# Add backend/app to path regardless of where pytest runs
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from pnl_calculator import calculate_credit_spread_pnl, calculate_iron_condor_width

def test_call_credit_max_gain():
    result = calculate_credit_spread_pnl(short_strike=600, long_strike=610, net_credit=2.5, is_call=True)
    assert result["max_gain"] == 2.5
    assert result["max_loss"] == 7.5
    assert result["width"] == 10
    assert result["breakeven"] == 602.5

def test_put_credit_max_gain():
    result = calculate_credit_spread_pnl(short_strike=590, long_strike=580, net_credit=1.8, is_call=False)
    assert result["max_gain"] == 1.8
    assert result["width"] == 10
    assert result["breakeven"] == 588.2

def test_credit_exceeds_width_rejected():
    with pytest.raises(ValueError):
        calculate_credit_spread_pnl(600, 610, 15, True)

def test_pnl_points_generated():
    result = calculate_credit_spread_pnl(600, 610, 2.5, True)
    assert len(result["points"]) == 51
    assert result["points"][0]["pnl"] == 2.5
    assert result["points"][-1]["pnl"] == -7.5

def test_iron_condor_width():
    result = calculate_iron_condor_width(short_call=610, long_call=620, short_put=580, long_put=570)
    assert result["call_width"] == 10
    assert result["put_width"] == 10
    assert result["max_width"] == 10
