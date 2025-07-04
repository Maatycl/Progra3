# api/schemas.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ClientSchema(BaseModel):
    id: str
    name: str
    location: str
    total_orders: int

    class Config:
        orm_mode = True


class OrderSchema(BaseModel):
    id: str
    client_name: str
    client_id: str
    origin: str
    destination: str
    cost: float
    priority: int
    status: str
    created_at: str
    delivered_at: Optional[str] = None

    class Config:
        orm_mode = True


class SummarySchema(BaseModel):
    total_orders: int
    total_clients: int
    total_distance: float
    avg_order_cost: float
    max_order_cost: float
    min_order_cost: float


class RankingItemSchema(BaseModel):
    name: str
    visits: int

class RankingListSchema(BaseModel):
    rankings: List[RankingItemSchema]
