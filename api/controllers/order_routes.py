from fastapi import APIRouter, HTTPException
from typing import List
from api.schemas import OrderSchema
from api.global_simulation import get as get_simulation

router = APIRouter()

@router.get("/orders/", response_model=List[OrderSchema], summary="Obtener todas las órdenes")
def get_all_orders():
    sim = get_simulation()
    if sim is None or not sim.get_all_orders():
        raise HTTPException(status_code=404, detail="No hay simulación activa o no hay órdenes registradas.")

    orders = sim.get_all_orders()
    return [
        OrderSchema(
            id=str(order.id),
            client_name=order.client.name,
            client_id=order.client.id,
            origin=str(order.origin),
            destination=str(order.destination),
            cost=order.cost,
            priority=order.priority,
            status=order.status,
            created_at=order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            delivered_at=order.delivered_at.strftime("%Y-%m-%d %H:%M:%S") if order.delivered_at else None
        ) for order in orders
    ]
