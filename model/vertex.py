# Representa un vértice simple en un grafo
class Vertex:
    """Lightweight vertex structure for a graph."""
    __slots__ = '_element' # Optimiza el uso de memoria

    def __init__(self, element):
        # Almacena el valor asociado al vértice (ej. etiqueta, nombre, etc.)
        """Do not call constructor directly. Use Graph's insert_vertex(element)."""
        self._element = element

    def element(self):
        """Return element associated with this vertex."""
        return self._element

    def __hash__(self):
        # Permite usar el vértice como clave en diccionarios/sets
        return hash(id(self))

    def __str__(self):
        # Representación en texto (útil para mostrar en pantalla)
        return str(self._element)

    def __repr__(self):
        # Representación oficial (debug/logs)
        return f"Vertex({self._element})"
