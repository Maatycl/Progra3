import random
from sim.simulation_initializer import SimulationInitializer
from domain.client import Client
from domain.order import Order

AUTONOMY_LIMIT = 50  # Máxima distancia que un dron puede recorrer sin recarga

# Clase principal que gestiona la simulación
class Simulation:
    def __init__(self, n_nodes=15, m_edges=20):
        # Inicializa el grafo y roles con el generador
        self.initializer = SimulationInitializer(n_nodes, m_edges)
        self.graph, self.vertex_roles = self.initializer.generate_graph()
        self.orders = [] # Lista de órdenes creadas
        self.route_log = [] # Historial de rutas usadas
        self.clients = {} # Diccionarios de clientes por ID

    def generate_order(self):
        # Filtra nodos de origen (almacenamiento) y destino (clientes)
        """Genera una orden entre un nodo de almacenamiento y un cliente"""
        origins = [v for v in self.graph.vertices() if "Almacenamiento" in self.vertex_roles[v]]
        destinations = [v for v in self.graph.vertices() if "Cliente" in self.vertex_roles[v]]

        if not origins or not destinations:
            return None
        
        # Selecciona nodos aleatorios para crear orden
        origin = random.choice(origins)
        destination = random.choice(destinations)

        # Busca ruta entre origen y destino
        path, cost = self.find_route(origin, destination)
        if not path:
            return None

        # Crea cliente si no existe
        client_id = str(destination)
        if client_id not in self.clients:
            self.clients[client_id] = Client(client_id, f"Cliente {client_id}", destination)
        client = self.clients[client_id]
        client.register_order()

        # Crea y almacena la orden
        order = Order(
            client=client,
            origin=origin,
            destination=destination,
            path=path,
            cost=cost
        )

        self.orders.append(order)
        self.route_log.append(path)
        return order

    
    def find_route(self, origin, destination):
        """Busca ruta entre origen y destino respetando autonomía, usando recarga si es necesario."""

        def dfs(v, target, visited, path, cost):
            # Ruta inválida si excede autonomía
            if cost > AUTONOMY_LIMIT:
                return None
            visited.add(v)
            path.append(v)
            if v == target:
                return list(path)
            for neighbor in self.graph.neighbors(v):
                if neighbor not in visited:
                    edge = self.graph.get_edge(v, neighbor)
                    result = dfs(neighbor, target, visited, path, cost + edge.element())
                    if result:
                        return result
            path.pop()
            visited.remove(v)
            return None

        # 1. Ruta directa primero
        path = dfs(origin, destination, set(), [], 0)
        if path:
            total_cost = sum(self.graph.get_edge(path[i], path[i+1]).element() for i in range(len(path) - 1))
            return path, total_cost

        # 2. Si no hay ruta directa, probar con nodos de recarga
        recharge_nodes = [v for v in self.graph.vertices() if "Recarga" in self.vertex_roles[v]]

        for r1 in recharge_nodes:
            path1 = dfs(origin, r1, set(), [], 0)
            if not path1:
                continue
            path2 = dfs(r1, destination, set(), [], 0)
            if not path2:
                continue
            full_path = path1 + path2[1:]  # evitar repetir r1
            total_cost = sum(self.graph.get_edge(full_path[i], full_path[i+1]).element() for i in range(len(full_path) - 1))
            return full_path, total_cost

        return None, None

    # Métodos auxiliares para acceso a datos
    def get_roles(self):
        return self.vertex_roles

    def get_graph(self):
        return self.graph

    def get_all_orders(self):
        return self.orders

    def get_clients(self):
        return list(self.clients.values())
