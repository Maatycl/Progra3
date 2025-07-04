from .vertex import Vertex
from .edge import Edge
import heapq

class Graph:
    def __init__(self, directed=False):
        self._outgoing = {}
        self._incoming = {} if directed else self._outgoing
        self._directed = directed

    def is_directed(self):
        return self._directed

    def insert_vertex(self, element):
        v = Vertex(element)
        self._outgoing[v] = {}
        if self._directed:
            self._incoming[v] = {}
        return v

    def insert_edge(self, u, v, element):
        e = Edge(u, v, element)
        self._outgoing[u][v] = e
        self._incoming[v][u] = e
        return e

    def remove_edge(self, u, v):
        if u in self._outgoing and v in self._outgoing[u]:
            del self._outgoing[u][v]
            del self._incoming[v][u]

    def remove_vertex(self, v):
        for u in list(self._outgoing.get(v, {})):
            self.remove_edge(v, u)
        for u in list(self._incoming.get(v, {})):
            self.remove_edge(u, v)
        self._outgoing.pop(v, None)
        if self._directed:
            self._incoming.pop(v, None)

    def get_edge(self, u, v):
        return self._outgoing.get(u, {}).get(v)

    def vertices(self):
        return self._outgoing.keys()

    def edges(self):
        seen = set()
        for map in self._outgoing.values():
            seen.update(map.values())
        return seen

    def neighbors(self, v):
        return self._outgoing[v].keys()

    def degree(self, v, outgoing=True):
        adj = self._outgoing if outgoing else self._incoming
        return len(adj[v])

    def incident_edges(self, v, outgoing=True):
        adj = self._outgoing if outgoing else self._incoming
        return adj[v].values()

    def dijkstra_shortest_path(self, start, end):
        """Calcula el camino más corto de start a end usando Dijkstra.
        Devuelve (ruta, costo) o (None, inf) si no existe camino.
        """
        distances = {vertex: float('inf') for vertex in self.vertices()}
        previous = {vertex: None for vertex in self.vertices()}
        distances[start] = 0
        visited = set()
        heap = [(0, start)]

        while heap:
            current_distance, current_vertex = heapq.heappop(heap)
            if current_vertex in visited:
                continue
            visited.add(current_vertex)

            if current_vertex == end:
                break

            for neighbor in self.neighbors(current_vertex):
                edge = self.get_edge(current_vertex, neighbor)
                if edge is None:
                    continue
                weight = edge.element()
                distance = current_distance + weight
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current_vertex
                    heapq.heappush(heap, (distance, neighbor))

        # Reconstruir ruta
        path = []
        current = end
        if previous[current] is None and current != start:
            return None, float('inf')  # no hay ruta

        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()

        return path, distances[end]
