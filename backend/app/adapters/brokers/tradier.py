
import os, random, httpx
from .base import BrokerAdapter
from typing import List, Dict

class TradierAdapter(BrokerAdapter):
    def __init__(self):
        self.api_key = os.getenv("TRADIER_API_KEY", "mock")
        self.account_id = os.getenv("TRADIER_ACCOUNT_ID", "mock_account")
        self.is_mock = self.api_key == "mock"

    async def place_order(self, order) -> Dict:
        if self.is_mock:
            return {
                "id": f"trad_mock_{random.randint(10000,99999)}",
                "status": "filled",
                "avg_price": round(random.uniform(0.6, 0.85), 2),
                "filled_qty": order.qty,
                "broker": "tradier_mock",
                "dry_run": True
            }
        return {"id": "real", "status": "filled"}

    async def get_positions(self) -> List[Dict]:
        if self.is_mock:
            return [
                {
                    "id": "pos_spx_1",
                    "symbol": "SPX 5850/5860 Call Credit 0DTE",
                    "underlying": "SPX",
                    "type": "CALL_CREDIT_SPREAD",
                    "qty": 1,
                    "avg_cost": 0.78,
                    "current_price": round(random.uniform(0.55, 0.75), 2),
                    "market_value": 65,
                    "day_pnl": 13,
                    "total_pnl": 13,
                    "occ_symbols": ["SPX 260923C05850000", "SPX 260923C05860000"]
                },
                {
                    "id": "pos_spy_1",
                    "symbol": "SPY 580/585 Put Credit",
                    "underlying": "SPY",
                    "type": "PUT_CREDIT_SPREAD",
                    "qty": 2,
                    "avg_cost": 0.45,
                    "current_price": 0.30,
                    "market_value": 60,
                    "day_pnl": 30,
                    "total_pnl": 45,
                    "occ_symbols": ["SPY 260923P00580000"]
                }
            ]
        return []

    async def get_quotes(self, symbols: List[str]) -> Dict:
        return {s: {"bid": 0.65, "ask": 0.85, "mid": 0.75, "last": 0.73} for s in symbols}

    async def get_option_chain(self, underlying: str, dte: int = 0) -> Dict:
        base_price = {"SPX": 5847.12, "SPY": 584.20, "QQQ": 485.10}.get(underlying, 5000)
        strikes = []
        for i in range(-10, 11):
            strike = base_price + (i * (5 if underlying=="SPX" else 1))
            strikes.append({
                "strike": round(strike),
                "call_bid": round(max(0.1, 2.5 - abs(i)*0.15),2),
                "call_ask": round(max(0.15, 2.7 - abs(i)*0.15),2),
                "put_bid": round(max(0.1, 2.5 - abs(i)*0.15),2),
                "put_ask": round(max(0.15, 2.7 - abs(i)*0.15),2),
                "delta": round(0.5 - i*0.05, 2)
            })
        return {
            "underlying": underlying,
            "underlying_price": base_price,
            "dte": dte,
            "strikes": strikes,
            "atm": round(base_price / (5 if underlying=="SPX" else 1)) * (5 if underlying=="SPX" else 1)
        }

    async def close_position(self, position_id: str, qty: int = None) -> Dict:
        return {"id": f"close_{position_id}", "status": "filled", "avg_price": 0.30, "closed_qty": qty or 1}
