# Representa un vértice simple en un grafo
class Vertex:
    """Lightweight vertex structure for a graph."""
    __slots__ = '_element'  # Optimiza el uso de memoria

    def __init__(self, element):
        """No llamar directamente. Usa insert_vertex(element) del grafo."""
        self._element = element

    def element(self):
        """Retorna el elemento asociado a este vértice."""
        return self._element

    def __hash__(self):
        """Permite usar el vértice como clave en diccionarios/sets."""
        return hash(id(self))

    def __str__(self):
        """Representación en texto amigable."""
        return str(self._element)

    def __repr__(self):
        """Representación oficial para debugging."""
        return f"Vertex({self._element})"

    def __lt__(self, other):
        """Define orden entre vértices para que heapq funcione correctamente."""
        return str(self._element) < str(other._element)

