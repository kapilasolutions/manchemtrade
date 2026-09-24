
import time
class Ledger:
    def __init__(self):
        self.webhooks = []
        self.orders = []
    def add_webhook(self, payload: dict):
        self.webhooks.append({**payload, "received_at": time.time(), "id": f"wh_{len(self.webhooks)+1}"})
    def add_order(self, order: dict):
        self.orders.append({**order, "created_at": time.time(), "id": f"ord_{len(self.orders)+1}"})
        return self.orders[-1]
ledger = Ledger()
