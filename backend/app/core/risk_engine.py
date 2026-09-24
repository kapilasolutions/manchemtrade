
from typing import Dict
class RiskEngine:
    def __init__(self):
        self.daily_loss_limit = 500
        self.max_contracts_per_trade = 10
        self.kill_switch = False
        self.daily_pnl = 120
    def check(self, order) -> Dict:
        if self.kill_switch:
            return {"allowed": False, "reason": "Kill switch active"}
        if order.qty > self.max_contracts_per_trade:
            return {"allowed": False, "reason": f"Qty {order.qty} > max {self.max_contracts_per_trade}"}
        if self.daily_pnl < -self.daily_loss_limit:
            return {"allowed": False, "reason": f"Daily loss limit {self.daily_loss_limit} hit"}
        return {"allowed": True, "reason": "OK"}
    def trigger_kill(self):
        self.kill_switch = True
    def resume(self):
        self.kill_switch = False
risk_engine = RiskEngine()
