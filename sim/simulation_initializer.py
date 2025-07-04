import random
from model.graph import Graph
from model.vertex import Vertex

# Roles disponibles
NODE_STORAGE = "📦 Almacenamiento"
NODE_RECHARGE = "🔋 Recarga"
NODE_CLIENT = "👤 Cliente"

# Clase que inicializa la simulación y genera el grafo
class SimulationInitializer:
    def __init__(self, n_nodes, m_edges, directed=False):
        # Inicializa con nodos, aristas mínimas y tipo de grafo
        self.n_nodes = n_nodes
        self.m_edges = max(m_edges, n_nodes - 1)  # asegura conectividad
        self.graph = Graph(directed) # Grafo vacío
        self.vertex_roles = {} # Diccionario de roles por nodo

    def generate_labels(self, n):
        from string import ascii_uppercase
        labels = []
        i = 0
        while len(labels) < n:
            label = ""
            temp = i
            while True:
                label = ascii_uppercase[temp % 26] + label
                temp = temp // 26 - 1
                if temp < 0:
                    break
            labels.append(label)
            i += 1
        return labels


    def generate_roles(self):
        # 20% almacenamiento, 20% recarga, 60% clientes
        """Asigna roles según proporciones fijas"""
        n_storage = self.n_nodes * 20 // 100
        n_recharge = self.n_nodes * 20 // 100
        n_client = self.n_nodes - n_storage - n_recharge

        roles = (
            [NODE_STORAGE] * n_storage +
            [NODE_RECHARGE] * n_recharge +
            [NODE_CLIENT] * n_client
        )
        random.shuffle(roles) # Mezcla aleatoria de roles
        return roles

    def generate_graph(self):
        """Genera un grafo conexo con nodos y aristas aleatorias"""
        roles = self.generate_roles()
        vertices = []

        # Crear vértices con rol
        labels = self.generate_labels(self.n_nodes)
        for i in range(self.n_nodes):
            label = labels[i]  # A, B, ..., Z, N26...
            v = self.graph.insert_vertex(label)
            self.vertex_roles[v] = roles[i]
            vertices.append(v)

        # Conectividad mínima: árbol generador aleatorio
        connected = [vertices[0]]
        remaining = vertices[1:]
        while remaining:
            u = random.choice(connected)
            v = random.choice(remaining)
            weight = random.randint(1, 20)
            self.graph.insert_edge(u, v, weight)
            connected.append(v)
            remaining.remove(v)

        # Agregar aristas adicionales
        added_edges = self.n_nodes - 1
        while added_edges < self.m_edges:
            u, v = random.sample(vertices, 2)
            if not self.graph.get_edge(u, v) and u != v:
                weight = random.randint(1, 20)
                self.graph.insert_edge(u, v, weight)
                added_edges += 1

        # Devuelve el grafo completo y roles asignados
        return self.graph, self.vertex_roles
