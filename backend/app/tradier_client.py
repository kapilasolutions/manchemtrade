
"""
Tradier Client with DRY_RUN toggle - ManchemTrade v3.8.5
Feature #3: Real Tradier vs Mock toggle
"""
import os
import time
from typing import Dict, Optional
from datetime import datetime

# Config from env
DRY_RUN = os.getenv("DRY_RUN", "true").lower() in ("true", "1", "yes")
TRADIER_TOKEN = os.getenv("TRADIER_TOKEN", "")
TRADIER_BASE = "https://api.tradier.com/v1"

def is_market_hours() -> bool:
    """Check if US market is open (simplified: 9:30-16:00 ET Mon-Fri)"""
    now = datetime.now()
    # For POC, just check weekday - real would check ET time
    return now.weekday() < 5

def generate_tight_mock(ticker: str) -> Dict:
    """Mock generator - never returns undefined (from v3.8.3)"""
    base_prices = {"SPX": 600, "SPY": 590, "QQQ": 520, "AAPL": 240, "TSLA": 400, "NVDA": 150, "MSFT": 430, "GOOGL": 200}
    base = base_prices.get(ticker.upper(), 100)
    strikes = []
    for i in range(-10, 11):
        strike = base + i*5
        bid = round(1.5 + abs(i)*0.1, 2)
        ask = round(bid + 0.15, 2)
        mid = round((bid+ask)/2, 2)
        strikes.append({
            "strike": strike,
            "bid": bid,
            "ask": ask,
            "mid": mid,
            "iv": round(0.2 + abs(i)*0.01, 3),
            "delta": round(0.5 - i*0.05, 3)
        })
    return {
        "ticker": ticker.upper(),
        "underlying_price": float(base),
        "strikes": strikes,
        "source": "mock",
        "timestamp": datetime.now().isoformat()
    }

def is_fake_chain(data: Dict) -> bool:
    """Reject empty or undefined chains"""
    if not data or not data.get("strikes"):
        return True
    for s in data["strikes"]:
        if "undefined" in str(s.get("bid", "")).lower() or "undefined" in str(s.get("mid", "")).lower():
            return True
        try:
            if float(s.get("mid", 0)) <= 0:
                return True
        except:
            return True
    return False

def fetch_tradier_chain(ticker: str, expiry: Optional[str] = None) -> Dict:
    """
    Fetch from Tradier if DRY_RUN=false and token present, else fallback to mock.
    Handles market-closed and invalid token gracefully.
    """
    ticker = ticker.upper().strip()
    
    # Validate ticker - reject JUNK
    if not ticker.isalpha() or len(ticker) > 6 or len(ticker) < 1:
        raise ValueError(f"Invalid ticker: {ticker}")

    if DRY_RUN:
        print(f"[DRY_RUN] Using mock for {ticker}")
        return generate_tight_mock(ticker)

    if not TRADIER_TOKEN:
        print(f"[WARN] No TRADIER_TOKEN, fallback to mock for {ticker}")
        return generate_tight_mock(ticker)

    # Try real Tradier API
    try:
        import httpx
        # Simplified - real would need expiry lookup
        url = f"{TRADIER_BASE}/markets/options/chains"
        params = {"symbol": ticker, "greeks": "true"}
        if expiry:
            params["expiration"] = expiry
        
        headers = {"Authorization": f"Bearer {TRADIER_TOKEN}", "Accept": "application/json"}
        
        resp = httpx.get(url, params=params, headers=headers, timeout=10)
        
        if resp.status_code == 401:
            print(f"[ERROR] Invalid Tradier token, fallback to mock")
            return generate_tight_mock(ticker)
        
        if resp.status_code == 200:
            data = resp.json()
            # Parse Tradier response (simplified)
            options = data.get("options", {}).get("option", [])
            if not options:
                print(f"[WARN] Empty chain from Tradier, fallback to mock")
                return generate_tight_mock(ticker)
            
            strikes = []
            for opt in options[:21]:  # limit
                try:
                    strikes.append({
                        "strike": float(opt.get("strike", 0)),
                        "bid": float(opt.get("bid", 0)),
                        "ask": float(opt.get("ask", 0)),
                        "mid": (float(opt.get("bid", 0)) + float(opt.get("ask", 0))) / 2,
                        "iv": float(opt.get("greeks", {}).get("mid_iv", 0.2)),
                        "delta": float(opt.get("greeks", {}).get("delta", 0))
                    })
                except:
                    continue
            
            if not strikes or is_fake_chain({"strikes": strikes}):
                return generate_tight_mock(ticker)
            
            return {
                "ticker": ticker,
                "underlying_price": float(strikes[len(strikes)//2]["strike"]),
                "strikes": strikes,
                "source": "tradier",
                "timestamp": datetime.now().isoformat()
            }
        else:
            print(f"[WARN] Tradier {resp.status_code}, fallback to mock")
            return generate_tight_mock(ticker)
            
    except Exception as e:
        print(f"[ERROR] Tradier fetch failed: {e}, fallback to mock")
        return generate_tight_mock(ticker)

def get_chain(ticker: str, expiry: Optional[str] = None) -> Dict:
    """Public API - handles DRY_RUN toggle + fallback"""
    return fetch_tradier_chain(ticker, expiry)
