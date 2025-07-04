import uuid
from datetime import datetime

# Representa una orden de entrega en el sistema logístico
class Order:
    def __init__(self, order_id=None, client=None, origin=None, destination=None, path=None, cost=0.0, priority=1):
        """
        Representa una orden de entrega.

        - order_id: identificador único de la orden (UUID por defecto)
        - client: instancia de Client
        - origin: vértice de origen
        - destination: vértice de destino
        - path: lista de vértices que representa la ruta seguida
        - cost: costo total de la ruta (suma de pesos)
        - priority: prioridad de entrega (1 por defecto)
        """
        self.id = order_id or str(uuid.uuid4()) # ID único de la orden
        self.client = client                    # Cliente que solicitó la orden
        self.origin = origin                    # Nodo origen
        self.destination = destination          # Nodo destino
        self.path = path                        # Ruta real, con nodos intermedios
        self.cost = cost                        # Costo de ruta
        self.priority = priority                # Prioridad de entrega
        self.status = "Pendiente"               # Estado Inicial
        self.created_at = datetime.now()        # Fecha/hora de creación
        self.delivered_at = None                # Fecha/hora de entrega

    def to_dict(self):
        """Devuelve una representación en formato diccionario (ideal para JSON o Streamlit)."""
        return {
            "id": self.id,
            "client_name": self.client.name,
            "client_id": self.client.id,
            "origin": str(self.origin),
            "destination": str(self.destination),
            "cost": self.cost,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "delivered_at": self.delivered_at.strftime("%Y-%m-%d %H:%M:%S") if self.delivered_at else None
        }

    def __str__(self):
        return f"Orden {self.id} | {self.origin} → {self.destination} | Costo: {self.cost} | Cliente: {self.client.name}"
