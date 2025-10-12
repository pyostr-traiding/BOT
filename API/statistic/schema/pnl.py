from pydantic import BaseModel


class PNLSchema(BaseModel):
    """
    Схема P&L расчета
    """

    total: float
    profit: float
    loss: float
