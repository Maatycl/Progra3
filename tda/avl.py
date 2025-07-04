# Nodo individual del árbol AVL
class AVLNode:
    def __init__(self, key, value):
        self.key = key      # Generalmente una instancia de Route
        self.value = value  # Puede ser la misma instancia o frecuencia
        self.left = None # Hijo izquierdo
        self.right = None # Hijo derecho
        self.height = 1 # Altura inicial

# Árbol AVL con inserción balanceada
class AVLTree:
    def __init__(self):
        self.root = None # Raiz del árbol

    ### --- API pública --- ###
    def insert(self, key, value=None):
        # Inserta clave y valor en el árbol
        self.root = self._insert(self.root, key, value)

    def get_in_order(self):
        """Devuelve una lista ordenada (clave, valor)"""
        result = []
        self._in_order(self.root, result)
        return result

    ### --- Métodos internos --- ###
    def _height(self, node):
        # Altura del nodo o 0 si es None
        return node.height if node else 0

    def _balance_factor(self, node):
        # Calcula el factor de balance
        return self._height(node.left) - self._height(node.right) if node else 0

    def _update_height(self, node):
        # Actualiza altura del nodo según hijos
        node.height = 1 + max(self._height(node.left), self._height(node.right))

    def _rotate_right(self, y):
        # Rotación simple a la derecha
        x = y.left
        T2 = x.right
        x.right = y
        y.left = T2
        self._update_height(y)
        self._update_height(x)
        return x

    def _rotate_left(self, x):
        # Rotación simple a la izquierda
        y = x.right
        T2 = y.left
        y.left = x
        x.right = T2
        self._update_height(x)
        self._update_height(y)
        return y

    def _balance(self, node):
        # Aplica rotaciones si el nodo está desbalanceado
        balance = self._balance_factor(node)

        # Rotación izquierda-derecha o simple derecha
        if balance > 1:
            if self._balance_factor(node.left) < 0:
                node.left = self._rotate_left(node.left)
            return self._rotate_right(node)

        # Rotación derecha-izquierda o simple izquierda
        if balance < -1:
            if self._balance_factor(node.right) > 0:
                node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    def _insert(self, node, key, value):
        if not node:
            return AVLNode(key, value)

        if key == node.key:
            node.value.freq += 1  # Aumenta frecuencia si es ruta repetida
        elif key < node.key:
            node.left = self._insert(node.left, key, value)
        else:
            node.right = self._insert(node.right, key, value)

        self._update_height(node)
        return self._balance(node)

    def _in_order(self, node, result):
        # Recorrido in-order: izquierda -> nodo -> derecha
        if node:
            self._in_order(node.left, result)
            result.append((node.key, node.value))
            self._in_order(node.right, result)
