
from abc import ABC, abstractmethod
from typing import List, Dict

class BrokerAdapter(ABC):
    @abstractmethod
    async def place_order(self, order) -> Dict:
        pass
    @abstractmethod
    async def get_positions(self) -> List[Dict]:
        pass
    @abstractmethod
    async def get_quotes(self, symbols: List[str]) -> Dict:
        pass
    @abstractmethod
    async def get_option_chain(self, underlying: str, dte: int = 0) -> Dict:
        pass
    def supports(self, asset_type: str) -> bool:
        return True
