
from fastapi import APIRouter
from app.adapters.brokers.tradier import TradierAdapter
router = APIRouter()
adapter = TradierAdapter()
@router.get("/chains/{underlying}")
async def get_chain(underlying: str, dte: int = 0):
    chain = await adapter.get_option_chain(underlying, dte)
    return chain
