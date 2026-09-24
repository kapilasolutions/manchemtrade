
from fastapi import APIRouter
from app.adapters.brokers.tradier import TradierAdapter
from app.services.ledger import ledger
router = APIRouter()
adapter = TradierAdapter()

@router.get("/positions")
async def get_positions(refresh: bool = False):
    positions = await adapter.get_positions()
    for p in positions:
        p["unrealized_pnl"] = round((p["avg_cost"] - p["current_price"]) * p["qty"] * 100, 2) if "Credit" in p["type"] else round((p["current_price"] - p["avg_cost"]) * p["qty"] * 100, 2)
    return {"positions": positions, "count": len(positions), "source": "tradier_mock" if adapter.is_mock else "tradier"}

@router.post("/positions/{position_id}/close")
async def close_position(position_id: str, qty: int = 1):
    result = await adapter.close_position(position_id, qty)
    ledger.add_order({**result, "source": "MANUAL_CLOSE", "position_id": position_id})
    return {"status": "closed", "position_id": position_id, "result": result}
