# Librerías necesarias para visualización del árbol
import matplotlib.pyplot as plt
import networkx as nx

# Clase para construir y visualizar el árbol AVL
class AVLVisualizer:
    def __init__(self):
        # Grafo dirigido (para mostrar relaciones padre-hijo)
        self.graph = nx.DiGraph()
        # Diccionarios para posición, etiquetas y estilos visuales
        self.pos = {}
        self.labels = {}
        self.font_sizes = {}
        self.node_sizes = {}

    def build(self, node, x=0, y=0, dx=1.5):
        """Construye el grafo recursivamente desde el nodo raíz del AVL"""
        if not node:
            return

        key_str = node.key.to_label() # Convierte clave a texto visible
        self.graph.add_node(key_str)  # Agrega nodo al grafo
        self.pos[key_str] = (x, y) # Posición en el plano
        self.labels[key_str] = key_str  #Etiqueta para mostrar

        # Ajuste dinámico de tamaño de fuente y nodo
        length = len(key_str)
        self.font_sizes[key_str] = max(6, 12 - (length // 5))   # Nunca menor que 6
        self.node_sizes[key_str] = min(6000, 1800 + length * 50)  # Nodo más grande si texto largo

         # Construir subárbol izquierdo
        if node.left:
            left_key = node.left.key.to_label()
            self.graph.add_edge(key_str, left_key)
            self.build(node.left, x - dx, y - 1, dx * 0.7)

        # Construir subárbol derecho
        if node.right:
            right_key = node.right.key.to_label()
            self.graph.add_edge(key_str, right_key)
            self.build(node.right, x + dx, y - 1, dx * 0.7)

    def draw(self, root):
        """Dibuja el árbol desde la raíz del AVL"""
        self.graph.clear()
        self.pos.clear()
        self.labels.clear()
        self.font_sizes.clear()
        self.node_sizes.clear()
        # Construir el grafo desde la raíz
        self.build(root)

        fig, ax = plt.subplots(figsize=(12, 6))

        # Dibujar nodos con tamaños individuales
        node_sizes = [self.node_sizes[n] for n in self.graph.nodes]
        nx.draw(
            self.graph,
            self.pos,
            with_labels=False, # Las etiquetas se dibujan manualmente
            node_color='skyblue',
            node_size=node_sizes,
            ax=ax,
            arrows=True
        )

        # Dibujar etiquetas manualmente
        for node, (x, y) in self.pos.items():
            ax.text(
                x, y,
                self.labels[node],
                fontsize=self.font_sizes[node],
                ha='center',
                va='center',
                fontweight='bold'
            )
        
        # Título y estilo del gráfico
        ax.set_title("AVL - Rutas más frecuentes", fontsize=14)
        plt.axis("off")
        plt.tight_layout()
        return fig
