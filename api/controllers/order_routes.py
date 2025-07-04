from fastapi import APIRouter, HTTPException
from typing import List
from api.schemas import OrderSchema
from api.global_simulation import get as get_simulation
from fastapi.responses import JSONResponse
from typing import List
from api.schemas import OrderSchema
from api.global_simulation import get as get_simulation
from datetime import datetime

router = APIRouter()

@router.get("/orders/", response_model=List[OrderSchema], summary="Obtener todas las órdenes")
def get_all_orders():
    sim = get_simulation()
    if sim is None or not sim.get_all_orders():
        raise HTTPException(status_code=404, detail="No hay simulación activa o no hay órdenes registradas.")
        raise HTTPException(status_code=404, detail="No hay simulación activa. Genera una en el dashboard primero.")

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

@router.get("/orders/orders/{order_id}", response_model=OrderSchema, summary="Obtener orden")
def get_order_by_id(order_id: str):
    sim = get_simulation()
    if sim is None or not sim.get_all_orders():
        raise HTTPException(status_code=404, detail="No hay simulación activa. Genera una en el dashboard primero.")

    order = next((o for o in sim.get_all_orders() if str(o.id) == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail=f"Orden con ID {order_id} no encontrada.")

    return OrderSchema(
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
    )

@router.post("/orders/orders/{order_id}/cancel", summary="Cancelar una orden")
def cancel_order(order_id: str):
    sim = get_simulation()
    if sim is None or not sim.get_all_orders():
        raise HTTPException(status_code=404, detail="No hay simulación activa. Genera una en el dashboard primero.")

    order = next((o for o in sim.get_all_orders() if str(o.id) == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail=f"Orden con ID {order_id} no encontrada.")

    if order.status != "Pendiente":
        raise HTTPException(status_code=400, detail=f"No se puede cancelar la orden con estado '{order.status}'.")

    order.status = "Cancelada"
    return JSONResponse(content={"message": f"Orden {order_id} cancelada correctamente."})

@router.post("/orders/orders/{order_id}/complete", summary="Completar una orden")
def complete_order(order_id: str):
    sim = get_simulation()
    if sim is None or not sim.get_all_orders():
        raise HTTPException(status_code=404, detail="No hay simulación activa. Genera una en el dashboard primero.")

    order = next((o for o in sim.get_all_orders() if str(o.id) == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail=f"Orden con ID {order_id} no encontrada.")

    if order.status != "Pendiente":
        raise HTTPException(status_code=400, detail=f"No se puede completar la orden con estado '{order.status}'.")

    order.status = "Entregado"
    order.delivered_at = datetime.now()
    return JSONResponse(content={"message": f"Orden {order_id} marcada como entregada correctamente."})