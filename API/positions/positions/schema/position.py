from typing import Literal, Optional, Any

from pydantic import BaseModel


class PositionSchema(BaseModel):
    """
    Схема позиции
    """
    symbol_name: str = 'BTCUSDT'
    uuid: str
    category: str = 'spot'
    side: Literal['buy', 'sell'] = 'buy'
    orderType: Literal[ 'Limit', 'Market',] = 'Limit'
    qty: str = '0.0002'
    price: str = '100000'
    takeProfit: Optional[str] = None
    stopLoss: Optional[str] = None
    kline_ms: int = 1233212
    status: str
    is_test: bool
    create_on: Any
