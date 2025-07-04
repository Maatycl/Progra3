from fastapi import APIRouter, HTTPException
from typing import List
from api.schemas import ClientSchema
from api.global_simulation import get as get_simulation

router = APIRouter()

@router.get("/clients/", response_model=List[ClientSchema], summary="Obtener todos los clientes")
def get_all_clients():
    sim = get_simulation()
    if sim is None or not sim.get_clients():
        raise HTTPException(status_code=404, detail="No hay simulación activa. Genera una en el dashboard primero.")
    
    clients = sim.get_clients()  # Método de tu simulación para obtener clientes
    return [
        ClientSchema(
            id=client.id,
            name=client.name,
            location=str(client.vertex),
            total_orders=client.total_orders
        ) for client in clients
    ]

@router.get("/clients/{client_id}", response_model=ClientSchema, summary="Obtener cliente")
def get_client_by_id(client_id: str):
    sim = get_simulation()
    if sim is None or not sim.get_clients():
        raise HTTPException(status_code=404, detail="No hay simulación activa. Genera una en el dashboard primero.")

    # Busca el cliente por ID
    client = next((c for c in sim.get_clients() if c.id == client_id), None)
    if not client:
        raise HTTPException(status_code=404, detail=f"Cliente con ID {client_id} no encontrado.")

    return ClientSchema(
        id=client.id,
        name=client.name,
        location=str(client.vertex),
        total_orders=client.total_orders
    )