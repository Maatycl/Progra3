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

        adjusted_path, adjusted_cost = self.find_route(origin, destination)
        if not adjusted_path:
            return None

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
        """Busca ruta usando Dijkstra como base, insertando recargas si se excede la autonomía, recalculando desde recargas."""
        current_node = origin
        adjusted_path = [current_node]
        current_cost = 0

        while True:
            # Calcular ruta actual hasta destino
            path, total_cost = self.graph.dijkstra_shortest_path(current_node, destination)
            if not path:
                return None, None

            for i in range(1, len(path)):
                u, v = path[i-1], path[i]
                edge_cost = self.graph.get_edge(u, v).element()
                current_cost += edge_cost

                if current_cost > AUTONOMY_LIMIT:
                    # Buscar recarga más cercana desde el nodo actual
                    recharge, _ = self.find_nearest_recharge(u, self.vertex_roles)
                    if recharge:
                        # Calcular ruta desde nodo actual a recarga
                        subpath, _ = self.graph.dijkstra_shortest_path(u, recharge)
                        if subpath is None or len(subpath) < 2:
                            return None, None
                        adjusted_path.extend(subpath[1:])
                        current_cost = 0
                        current_node = recharge  # reinicia cálculo desde recarga
                        break  # recalcula ruta desde recarga hacia destino
                    else:
                        return None, None  # No hay recarga accesible
                else:
                    adjusted_path.append(v)
                    current_node = v

            if current_node == destination:
                break  # destino alcanzado

        adjusted_cost = self.compute_total_cost(adjusted_path)
        return adjusted_path, adjusted_cost

    def find_nearest_recharge(self, node, roles):
        """Busca el nodo de recarga más cercano desde 'node'."""
        min_distance = float('inf')
        closest_recharge = None
        for v in self.graph.vertices():
            if "Recarga" in roles[v]:
                path, distance = self.graph.dijkstra_shortest_path(node, v)
                if path and distance < min_distance:
                    min_distance = distance
                    closest_recharge = v
        return closest_recharge, min_distance

    def compute_total_cost(self, path):
        total = 0
        for u, v in zip(path[:-1], path[1:]):
            edge = self.graph.get_edge(u, v)
            if edge is None:
                raise ValueError(f"No se encontró una arista entre {u} y {v}. Revisa la generación del grafo o el camino calculado.")
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
    
    def get_node_distribution(self):
        """Devuelve un dict con el conteo de nodos: {"Storage": x, "Recharge": y, "Clients": z}"""
        distribution = {"Storage": 0, "Recharge": 0, "Clients": 0}
        for v, roles in self.vertex_roles.items():
            if "Almacenamiento" in roles:
                distribution["Storage"] += 1
            elif "Recarga" in roles:
                distribution["Recharge"] += 1
            elif "Cliente" in roles:
                distribution["Clients"] += 1
        return distribution

    def get_top_visited_clients(self, top_n=6):
        """Devuelve lista [(client_id, total_orders)] de los clientes con más pedidos."""
        sorted_clients = sorted(
            self.clients.values(),
            key=lambda c: c.total_orders,
            reverse=True
        )
        return [(client.id, client.total_orders) for client in sorted_clients[:top_n]]

    def get_top_visited_recharges(self, top_n=4):
        """Devuelve lista [(recharge_node, visitas)] de las recargas más visitadas."""
        visit_count = {}
        for path in self.route_log:
            for node in path:
                if "Recarga" in self.vertex_roles.get(node, ""):
                    visit_count[node] = visit_count.get(node, 0) + 1
        sorted_visits = sorted(visit_count.items(), key=lambda x: x[1], reverse=True)
        return [(str(node), count) for node, count in sorted_visits[:top_n]]

    def get_top_visited_storage_nodes(self, top_n=4):
        """Devuelve lista [(storage_node, visitas)] de los almacenamientos más visitados."""
        visit_count = {}
        for path in self.route_log:
            for node in path:
                if "Almacenamiento" in self.vertex_roles.get(node, ""):
                    visit_count[node] = visit_count.get(node, 0) + 1
        sorted_visits = sorted(visit_count.items(), key=lambda x: x[1], reverse=True)
        return [(str(node), count) for node, count in sorted_visits[:top_n]]

    # Métodos auxiliares para acceso a datos
    def get_roles(self):
        return self.vertex_roles

    def get_graph(self):
        return self.graph

    def get_all_orders(self):
        return self.orders

    def get_clients(self):
        return list(self.clients.values())
