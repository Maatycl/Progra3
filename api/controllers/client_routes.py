from fastapi import APIRouter, HTTPException
from typing import List
from api.schemas import ClientSchema
from api.global_simulation import get as get_simulation

router = APIRouter()

@router.get("/clients/", response_model=List[ClientSchema], summary="Obtener todos los clientes")
def get_all_clients():
    sim = get_simulation()
    if sim is None or not sim.get_clients():
        raise HTTPException(status_code=404, detail="No hay simulación activa o no hay clientes registrados.")
    
    clients = sim.get_clients()  # Método de tu simulación para obtener clientes
    return [
        ClientSchema(
            id=client.id,
            name=client.name,
            location=str(client.vertex),
            total_orders=client.total_orders
        ) for client in clients
    ]