
from fastapi import APIRouter
router = APIRouter()
@router.get("/watchlists")
async def get_watchlists():
    return {
        "watchlists": [
            {"ticker": "SPX", "price": 5847.12, "change": 0.5, "iv_rank": 32},
            {"ticker": "SPY", "price": 584.20, "change": 0.3, "iv_rank": 28},
            {"ticker": "QQQ", "price": 485.10, "change": 0.6, "iv_rank": 30},
            {"ticker": "AAPL", "price": 250.10, "change": 1.2, "iv_rank": 45},
            {"ticker": "TSLA", "price": 260.50, "change": -0.8, "iv_rank": 65}
        ]
    }
