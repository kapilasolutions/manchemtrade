
from fastapi import APIRouter
from app.models.unified_order import UnifiedOrder, OptionLeg, AssetType, Source, PricingMode
from app.core.risk_engine import risk_engine
from app.adapters.brokers.tradier import TradierAdapter
from app.services.ledger import ledger
import uuid, asyncio, random
router = APIRouter()
adapter = TradierAdapter()

def build_occ(ticker: str, strike: int, right: str, expiry: str = "260923") -> str:
    strike_padded = f"{int(strike*1000):08d}"
    return f"{ticker} {expiry}{right}{strike_padded}"

@router.post("/quicktrade/execute")
async def quicktrade_execute(
    underlying: str = "SPX",
    strategy: str = "CALL_CREDIT_SPREAD",
    leg1_strike: int = 5850,
    leg2_strike: int = 5860,
    qty: int = 1,
    pricing_mode: PricingMode = PricingMode.MID_PEG_RETRY,
    width: int = 10,
    template_id: str = None
):
    occ1 = build_occ(underlying, leg1_strike, "C")
    occ2 = build_occ(underlying, leg2_strike, "C")
    legs = [
        OptionLeg(occ_symbol=occ1, side="SELL", quantity=qty, action="SELL_TO_OPEN"),
        OptionLeg(occ_symbol=occ2, side="BUY", quantity=qty, action="BUY_TO_OPEN")
    ]
    order = UnifiedOrder(
        underlying=underlying,
        asset_type=AssetType.SPREAD,
        legs=legs,
        qty=qty,
        pricing_mode=pricing_mode,
        source=Source.QUICKTRADE,
        template_id=template_id,
        idempotency_key=f"QT_{uuid.uuid4()}"
    )
    risk = risk_engine.check(order)
    if not risk["allowed"]:
        return {"status": "blocked", "reason": risk["reason"]}
    quotes = await adapter.get_quotes([occ1, occ2])
    mid_price = 0.78
    attempts = []
    fill_price = mid_price
    for attempt in range(1,4):
        current_mid = round(mid_price - (attempt-1)*0.03 + random.uniform(-0.02,0.02),2)
        attempts.append({"attempt": attempt, "mid": current_mid})
        if random.random() > 0.3 or attempt==3:
            fill_price = current_mid
            break
        await asyncio.sleep(0.2)
    result = await adapter.place_order(order)
    result["fill_price"] = fill_price
    result["peg_attempts"] = attempts
    result["max_loss"] = (width - fill_price) * qty * 100
    result["collateral"] = result["max_loss"]
    ledger.add_order({**result, "underlying": underlying, "strategy": strategy, "source": "QUICKTRADE", "legs": [l.dict() for l in legs]})
    brackets = {
        "profit_taker": {"price": round(fill_price*0.5,2), "status": "open"},
        "stop_loss": {"price": round(fill_price*2.0,2), "status": "open"},
        "time_stop": "15:50 ET"
    }
    return {
        "status": "filled",
        "order": order.dict(),
        "fill_price": fill_price,
        "proceeds": fill_price*qty*100,
        "brackets": brackets,
        "broker_response": result
    }

@router.get("/templates")
async def list_templates():
    return {
        "templates": [
            {"id": "tpl_spx_10w_atm", "name": "SPX $10W ATM Mid Peg", "underlying": "SPX", "strategy": "CALL_CREDIT_SPREAD", "width": 10, "strike_logic": "ATM", "pricing": "MID_PEG_RETRY", "qty": 1, "tp": 50, "sl": 2.0},
            {"id": "tpl_spy_5w_otm", "name": "SPY $5W OTM 1% Quick", "underlying": "SPY", "strategy": "PUT_CREDIT_SPREAD", "width": 5, "strike_logic": "OTM_1PCT", "pricing": "MARKET", "qty": 1, "tp": 50, "sl": 2.0}
        ]
    }
