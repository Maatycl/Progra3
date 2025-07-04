from fastapi import APIRouter, HTTPException
from api.schemas import RankingListSchema, RankingItemSchema, SummarySchema
from api.global_simulation import get as get_simulation
from collections import Counter

router = APIRouter()

@router.get("/info/reports/visits/clients", response_model=RankingListSchema, summary="Ranking de clientes más visitados")
def get_client_visits_ranking():
    sim = get_simulation()
    if sim is None or not sim.route_log:
        raise HTTPException(status_code=404, detail="No hay simulación activa. Genera una en el dashboard primero.")

    visits_counter = Counter()
    for path in sim.route_log:
        for node in path:
            if "Cliente" in sim.vertex_roles[node]:
                visits_counter[str(node)] += 1

    rankings = [
        RankingItemSchema(name=node, visits=visits)
        for node, visits in visits_counter.most_common()
    ]

    return RankingListSchema(rankings=rankings)

@router.get("/info/reports/visits/recharges", response_model=RankingListSchema, summary="Ranking de nodos de recarga más visitados")
def get_recharge_visits_ranking():
    sim = get_simulation()
    if sim is None or not sim.route_log:
        raise HTTPException(status_code=404, detail="No hay simulación activa. Genera una en el dashboard primero.")

    # Contar cuántas veces se visitó cada nodo de recarga en las rutas realizadas
    visits_counter = Counter()
    for path in sim.route_log:
        for node in path:
            if "Recarga" in sim.vertex_roles[node]:
                visits_counter[str(node)] += 1

    rankings = [
        RankingItemSchema(name=node, visits=visits)
        for node, visits in visits_counter.most_common()
    ]

    return RankingListSchema(rankings=rankings)

@router.get("/info/reports/visits/storages", response_model=RankingListSchema, summary="Ranking de nodos de almacenamiento más visitados")
def get_storage_visits_ranking():
    sim = get_simulation()
    if sim is None or not sim.route_log:
        raise HTTPException(status_code=404, detail="No hay simulación activa. Genera una en el dashboard primero.")

    # Contar cuántas veces se visitó cada nodo de almacenamiento en las rutas realizadas
    visits_counter = Counter()
    for path in sim.route_log:
        for node in path:
            if "Almacenamiento" in sim.vertex_roles[node]:
                visits_counter[str(node)] += 1

    rankings = [
        RankingItemSchema(name=node, visits=visits)
        for node, visits in visits_counter.most_common()
    ]

    return RankingListSchema(rankings=rankings)


@router.get("/info/reports/summary", response_model=SummarySchema, summary="Resumen general de la simulación")
def get_simulation_summary():
    sim = get_simulation()
    if sim is None or not sim.get_all_orders():
        raise HTTPException(status_code=404, detail="No hay simulación activa. Genera una en el dashboard primero.")

    orders = sim.get_all_orders()
    roles = sim.get_roles()
    total_orders = len(orders)
    total_clients = sum(1 for role in roles.values() if "Cliente" in role)
    total_recharges = sum(1 for role in roles.values() if "Recarga" in role)
    total_storages = sum(1 for role in roles.values() if "Almacenamiento" in role)
    total_distance = sum(order.cost for order in orders)
    avg_route_length = sum(len(order.path) for order in orders) / total_orders if total_orders else 0
    max_order_cost = max((order.cost for order in orders), default=0)
    min_order_cost = min((order.cost for order in orders), default=0)

    return SummarySchema(
    total_orders=total_orders,
    total_clients=total_clients,
    total_recharges=total_recharges,
    total_storages=total_storages,
    total_distance=total_distance,
    avg_route_length=avg_route_length,
    max_order_cost=max_order_cost,
    min_order_cost=min_order_cost
)