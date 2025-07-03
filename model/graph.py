from .vertex import Vertex
from .edge import Edge

# Representación de un grafo (dirigido o no dirigido)
class Graph:
    def __init__(self, directed=False):
        # Diccionario de adyacencia saliente
        self._outgoing = {}
        # Diccionario de adyacencia entrante (distinto solo si es dirigido)
        self._incoming = {} if directed else self._outgoing
        self._directed = directed # True si es grafo dirigido

    def is_directed(self):
        # Retorna True si el grafo es dirigido
        return self._directed

    def insert_vertex(self, element):
        # Crea vértice con valor y lo registra en la estructura
        v = Vertex(element)
        self._outgoing[v] = {}
        if self._directed:
            self._incoming[v] = {}
        return v

    def insert_edge(self, u, v, element):
        # Crea y agrega una arista entre u y v con el valor dado
        e = Edge(u, v, element)
        self._outgoing[u][v] = e
        self._incoming[v][u] = e
        return e

    def remove_edge(self, u, v):
        # Elimina arista entre u y v (si existe)
        if u in self._outgoing and v in self._outgoing[u]:
            del self._outgoing[u][v]
            del self._incoming[v][u]

    def remove_vertex(self, v):
        # Elimina el vértice v y todas sus aristas
        for u in list(self._outgoing.get(v, {})):
            self.remove_edge(v, u)
        for u in list(self._incoming.get(v, {})):
            self.remove_edge(u, v)
        self._outgoing.pop(v, None)
        if self._directed:
            self._incoming.pop(v, None)

    def get_edge(self, u, v):
        # Retorna la arista entre u y v (o None si no existe)
        return self._outgoing.get(u, {}).get(v)

    def vertices(self):
        # Retorna todos los vértices del grafo
        return self._outgoing.keys()

    def edges(self):
        # Retorna todas las aristas del grafo (sin duplicados)
        seen = set()
        for map in self._outgoing.values():
            seen.update(map.values())
        return seen

    def neighbors(self, v):
        # Retorna los vecinos del vértice v (adyacentes por salida)
        return self._outgoing[v].keys()

    def degree(self, v, outgoing=True):
        # Retorna el grado del vértice (saliente o entrante)
        adj = self._outgoing if outgoing else self._incoming
        return len(adj[v])

    def incident_edges(self, v, outgoing=True):
        # Retorna las aristas incidentes al vértice v
        adj = self._outgoing if outgoing else self._incoming
        return adj[v].values()
