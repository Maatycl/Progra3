# Representa una ruta tomada por el dron (lista de vértices)
class Route:
    def __init__(self, path):
        """
        path: lista de vértices que representan el recorrido del dron.
        """
        self.path = path # Lista ordenada de nodos recorridos
        self.freq = 1  # Frecuencia de uso de esta ruta

    def increment(self):
        """Aumenta la frecuencia cuando se reutiliza la ruta."""
        self.freq += 1

    def to_label(self):
        """Devuelve una representación de la ruta en texto para usar en gráficos."""
        return " → ".join(str(v) for v in self.path) + f" | Frecuencia: {self.freq}"

    def __str__(self):
        return f"Ruta: {' → '.join(str(v) for v in self.path)} (x{self.freq})"

    def __eq__(self, other):
        """Comparación por igualdad basada en los nodos del recorrido."""
        return isinstance(other, Route) and tuple(self.path) == tuple(other.path)

    def __hash__(self):
        """Permite usar rutas como claves en sets o diccionarios (por AVL)."""
        return hash(tuple(self.path))

    def __lt__(self, other):
        """Permite ordenar rutas lexicográficamente (por los nodos)."""
        return tuple(str(v) for v in self.path) < tuple(str(v) for v in other.path)
