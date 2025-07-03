import random
from sim.simulation_initializer import SimulationInitializer
from domain.client import Client
from domain.order import Order

AUTONOMY_LIMIT = 50  # Máxima distancia que un dron puede recorrer sin recarga

class Simulation:
    def __init__(self, n_nodes=15, m_edges=20):
        self.initializer = SimulationInitializer(n_nodes, m_edges)
        self.graph, self.vertex_roles = self.initializer.generate_graph()
        self.orders = []
        self.route_log = []
        self.clients = {}

    def generate_order(self):
        origins = [v for v in self.graph.vertices() if "Almacenamiento" in self.vertex_roles[v]]
        destinations = [v for v in self.graph.vertices() if "Cliente" in self.vertex_roles[v]]

        if not origins or not destinations:
            return None
        
        origin = random.choice(origins)
        destination = random.choice(destinations)

        path, cost = self.find_route(origin, destination)
        if not path:
            return None

        adjusted_path = self.enforce_autonomy_limit(path, self.vertex_roles)
        adjusted_cost = self.compute_total_cost(adjusted_path)

        client_id = str(destination)
        if client_id not in self.clients:
            self.clients[client_id] = Client(client_id, f"Cliente {client_id}", destination)
        client = self.clients[client_id]
        client.register_order()

        order = Order(
            client=client,
            origin=origin,
            destination=destination,
            path=adjusted_path,
            cost=adjusted_cost
        )

        self.orders.append(order)
        self.route_log.append(adjusted_path)
        return order

    def find_route(self, origin, destination):
        """Busca ruta directa con DFS, sin recarga."""
        def dfs(v, target, visited, path, cost):
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

        path = dfs(origin, destination, set(), [], 0)
        if path:
            total_cost = self.compute_total_cost(path)
            return path, total_cost

        # Sin ruta directa, intenta pasar por recargas manualmente
        recharge_nodes = [v for v in self.graph.vertices() if "Recarga" in self.vertex_roles[v]]
        for r1 in recharge_nodes:
            path1 = dfs(origin, r1, set(), [], 0)
            if not path1:
                continue
            path2 = dfs(r1, destination, set(), [], 0)
            if not path2:
                continue
            full_path = path1 + path2[1:]
            total_cost = self.compute_total_cost(full_path)
            return full_path, total_cost

        return None, None

    def enforce_autonomy_limit(self, path, roles, autonomy_limit=AUTONOMY_LIMIT):
        """Inserta nodos de recarga si la ruta excede la autonomía."""
        adjusted_path = []
        current_cost = 0
        last_node = path[0]
        adjusted_path.append(last_node)

        for i in range(1, len(path)):
            u, v = path[i-1], path[i]
            edge_cost = self.graph.get_edge(u, v).element()
            current_cost += edge_cost

            if current_cost > autonomy_limit:
                recharge = self.find_nearest_recharge(last_node, roles)
                if recharge and recharge not in adjusted_path:
                    adjusted_path.append(recharge)
                    current_cost = 0  # reinicia autonomía tras recarga
            adjusted_path.append(v)
            last_node = v

        return adjusted_path

    def find_nearest_recharge(self, node, roles):
        """Busca el nodo de recarga más cercano desde 'node'."""
        min_distance = float('inf')
        closest_recharge = None
        for v in self.graph.vertices():
            if "Recarga" in roles[v]:
                distance = self.graph.dijkstra_distance(node, v)
                if distance < min_distance:
                    min_distance = distance
                    closest_recharge = v
        return closest_recharge

    def compute_total_cost(self, path):
        """Calcula el costo total de una ruta ajustada."""
        total = 0
        for i in range(len(path) - 1):
            edge = self.graph.get_edge(path[i], path[i+1])
            total += edge.element()
        return total

    def compute_mst(self):
        """Calcula el Árbol de Expansión Mínima usando Kruskal y devuelve las aristas como pares (u, v)."""
        edges = []
        for edge in self.graph.edges():
            u, v = edge.endpoints()
            edges.append((edge.element(), u, v))

        edges.sort(key=lambda x: x[0])  # ordenar solo por peso
        parent = {}

        def find(v):
            while parent[v] != v:
                parent[v] = parent[parent[v]]
                v = parent[v]
            return v

        def union(u, v):
            pu, pv = find(u), find(v)
            if pu != pv:
                parent[pu] = pv

        for vertex in self.graph.vertices():
            parent[vertex] = vertex

        mst_edges = []
        for weight, u, v in edges:
            if find(u) != find(v):
                union(u, v)
                mst_edges.append((u, v))

        return mst_edges

    # Métodos auxiliares para acceso a datos
    def get_roles(self):
        return self.vertex_roles

    def get_graph(self):
        return self.graph

    def get_all_orders(self):
        return self.orders

    def get_clients(self):
        return list(self.clients.values())
