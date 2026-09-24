
from fastapi import APIRouter, Header, HTTPException
from app.models.unified_order import WebhookPayload, UnifiedOrder, OptionLeg, AssetType, Source, PricingMode
from app.core.risk_engine import risk_engine
from app.services.ledger import ledger
from app.adapters.brokers.tradier import TradierAdapter
router = APIRouter()
adapter = TradierAdapter()

@router.post("/webhook/{tenant_id}/{secret}")
async def receive_webhook(tenant_id: str, secret: str, payload: WebhookPayload, x_webhook_secret: str = Header(None)):
    if secret != payload.secret:
        raise HTTPException(status_code=401, detail="Secret mismatch")
    if any(o.get("idempotency_key") == payload.alert_id for o in ledger.orders):
        return {"status": "duplicate", "alert_id": payload.alert_id}
    ledger.add_webhook(payload.dict())
    legs = []
    if payload.legs:
        legs = payload.legs
    elif payload.occ_symbol:
        legs = [OptionLeg(occ_symbol=payload.occ_symbol, side="BUY", quantity=payload.quantity, action="BUY_TO_OPEN")]
    order = UnifiedOrder(
        underlying=payload.ticker,
        asset_type=AssetType.OPTION if payload.occ_symbol else AssetType.STOCK,
        legs=legs,
        qty=payload.quantity,
        pricing_mode=PricingMode.MARKET,
        source=Source.WEBHOOK,
        idempotency_key=payload.alert_id
    )
    risk = risk_engine.check(order)
    if not risk["allowed"]:
        raise HTTPException(status_code=400, detail=risk["reason"])
    result = await adapter.place_order(order)
    ledger.add_order({**result, "underlying": payload.ticker, "source": "WEBHOOK", "idempotency_key": payload.alert_id, "strategy_id": payload.strategy_id})
    return {"status": "executed", "broker_response": result, "order": order.dict()}
