# Representa un cliente dentro del sistema logístico
class Client:
    def __init__(self, client_id, name, vertex, client_type="normal"):
        """
        Representa un cliente en el sistema logístico.

        Parámetros:
        - client_id: identificador único del cliente.
        - name: nombre del cliente.
        - vertex: vértice del grafo asociado a su ubicación (objeto Vertex).
        """
        self.id = client_id # ID único del cliente
        self.name = name # Nombre del cliente
        self.vertex = vertex  # nodo en el grafo
        self.type = client_type
        self.total_orders = 0 # Cantidad de pedidos realizados

    def register_order(self):
        """Aumenta el contador de pedidos del cliente."""
        self.total_orders += 1

    def to_dict(self):
        """Devuelve los datos del cliente en formato diccionario."""
        return {
            "ID": self.id,
            "Nombre": self.name,
            "Ubicación": str(self.vertex),
            "Total Pedidos": self.total_orders
        }

    def __str__(self):
        return f"Cliente({self.id} - {self.name} - Nodo: {self.vertex})"

    def __repr__(self):
        return self.__str__()
