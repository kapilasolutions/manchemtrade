
from pydantic import BaseModel
from typing import Optional, List, Literal
from enum import Enum

class AssetType(str, Enum):
    STOCK = "STOCK"
    OPTION = "OPTION"
    SPREAD = "SPREAD"
    CRYPTO = "CRYPTO"
    FUTURES = "FUTURES"
    PREDICTION = "PREDICTION"

class Source(str, Enum):
    WEBHOOK = "WEBHOOK"
    QUICKTRADE = "QUICKTRADE"
    MANUAL_CLOSE = "MANUAL_CLOSE"

class PricingMode(str, Enum):
    MARKET = "MARKET"
    MID = "MID"
    MID_PEG_RETRY = "MID_PEG_RETRY"

class OptionLeg(BaseModel):
    occ_symbol: str
    side: Literal["BUY", "SELL"]
    quantity: int = 1
    action: Literal["BUY_TO_OPEN", "SELL_TO_OPEN", "BUY_TO_CLOSE", "SELL_TO_CLOSE"] = "BUY_TO_OPEN"

class UnifiedOrder(BaseModel):
    underlying: str
    asset_type: AssetType
    legs: List[OptionLeg]
    qty: int = 1
    pricing_mode: PricingMode = PricingMode.MARKET
    source: Source = Source.QUICKTRADE
    template_id: Optional[str] = None
    idempotency_key: str
    profit_target_pct: Optional[float] = 50.0
    stop_loss_x: Optional[float] = 2.0
    time_stop: Optional[str] = "15:50"

class WebhookPayload(BaseModel):
    secret: str
    action: str
    ticker: str
    occ_symbol: Optional[str] = None
    legs: Optional[List[OptionLeg]] = None
    quantity: int = 1
    order_type: str = "MARKET"
    strategy_id: Optional[str] = None
    alert_id: str
