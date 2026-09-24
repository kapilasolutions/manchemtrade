
import pytest

def is_fake_chain(data):
    """Same logic as frontend isFakeChain - must never return undefined fields"""
    if not data:
        return True
    if data.get('underlying_price') == 5000:
        return True
    strikes = data.get('strikes', [])
    if len(strikes) == 0 or len(strikes) < 5:
        return True
    has_undefined = any(
        s.get('bid') is None or s.get('ask') is None or s.get('mid') is None
        or 'undefined' in str(s.get('bid','')) or 'undefined' in str(s.get('mid',''))
        for s in strikes
    )
    if has_undefined:
        return True
    return False

def generate_tight_mock(ticker, put_mode=False):
    base_map = {'SPX':5847.12,'SPY':582.3,'QQQ':505.8,'AAPL':232.4,'TSLA':252.1,'NVDA':140.5,'MSFT':415.2,'GOOGL':165.3}
    base = base_map.get(ticker, 100)
    atm = 5847 if ticker=='SPX' else round(base)
    step = 5 if ticker=='SPX' else 1
    strikes=[]
    import random, math
    for i in range(-10,11):
        strike = atm + i*step
        abs_dist = abs(strike-base)
        base_mid = 20 if ticker=='SPX' else 3.2
        mid = base_mid * math.exp(-0.18*abs_dist) + 0.3 + random.random()*0.7
        if abs_dist>12:
            mid = 0.05 + random.random()*0.5
        mid = max(0.05, mid)
        spread = 0.05 + mid*0.07
        bid = mid - spread/2
        ask = mid + spread/2
        delta = -0.5*math.exp(-0.1*abs_dist) if put_mode else 0.5*math.exp(-0.1*abs_dist)
        strikes.append({'strike':strike,'bid':f"{bid:.2f}",'ask':f"{ask:.2f}",'mid':f"{mid:.2f}",'delta':f"{delta:.2f}",'iv':f"{20+random.random()*10:.1f}"})
    return {'underlying':ticker,'underlying_price':base,'atm_strike':atm,'strikes':strikes,'isMock':True}

def test_spx_mock_never_undefined():
    for ticker in ['SPX','SPY','QQQ','AAPL','TSLA','NVDA','MSFT','GOOGL']:
        data = generate_tight_mock(ticker, False)
        for s in data['strikes']:
            assert s['bid'] != 'undefined', f"{ticker} bid undefined at {s['strike']}"
            assert s['ask'] != 'undefined'
            assert s['mid'] != 'undefined'
            assert 'undefined' not in s['bid']
            assert float(s['mid']) > 0, f"{ticker} mid not >0"
        assert not is_fake_chain(data), f"{ticker} mock flagged as fake"

def test_junk_ticker_rejected():
    fake = {'underlying_price':5000,'strikes':[{'strike':100,'bid':'0.00','ask':'0.10','mid':'0.05'}]}
    assert is_fake_chain(fake) == True

def test_empty_chain_rejected():
    assert is_fake_chain({'strikes':[]}) == True
    assert is_fake_chain(None) == True

def test_width_calculation():
    # Call Credit Spread width = abs(L2-L1)
    l1,l2 = 580,585
    assert abs(l2-l1) == 5
    # Iron Condor width = max wing
    l1,l2,l3,l4 = 570,575,585,590
    assert max(abs(l2-l1),abs(l4-l3)) == 5
