# Librerías de interfaz y visualización
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import plotly.express as px
import pandas as pd
import networkx as nx
import json
from sim.simulation import Simulation
from visual.avl_visualizer import AVLVisualizer
from domain.route import Route
from tda.avl import AVLTree
from collections import Counter
from datetime import datetime
from domain.order import Order
from domain.client import Client

# Configura título y diseño ancho para la app
st.set_page_config(page_title="Sistema Logístico Autónomo", layout="wide")

tabs = st.tabs([
    "🔄 Run Simulation",
    "🌍 Explore Network",
    "🌐 Clients & Orders",
    "📋 Route Analytics",
    "📈 General Statistics"
])

# ----------------- Pestaña 0: Simulación ------------------
with tabs[0]:
    st.markdown("## 🔄 Simulación de Red Logística")
    st.markdown("Ajusta los parámetros y ejecuta la simulación para generar la red.")

    # Sliders para elegir nodos, aristas y órdenes
    col1, col2, col3 = st.columns(3)
    with col1:
        n_nodes = st.slider("🔢 Número de nodos", 10, 150, 15)
    with col2:
        m_edges = st.slider("🔗 Número de aristas", 10, 300, 20)
    with col3:
        n_orders = st.slider("📦 Número de órdenes", 10, 500, 10)

    # Detalle de roles usados en los nodos
    st.divider()
    st.markdown("### 📊 Proporción de Roles (automática)")
    st.markdown("- 📦 **Almacenamiento**: 20%")
    st.markdown("- 🔋 **Recarga**: 20%")
    st.markdown("- 👤 **Clientes**: 60%")

    # Inicia simulación con los parámetros seleccionados
    st.divider()
    if st.button("🚀 Iniciar Simulación", use_container_width=True):
        sim = Simulation(n_nodes, m_edges)
        for _ in range(n_orders):
            sim.generate_order()

        roles = sim.get_roles()
        total = len(roles)
        storage = sum(1 for r in roles.values() if "Almacenamiento" in r)
        recharge = sum(1 for r in roles.values() if "Recarga" in r)
        client = sum(1 for r in roles.values() if "Cliente" in r)

        st.success("✅ Simulación generada exitosamente.")
        col1, col2, col3 = st.columns(3)
        col1.metric("📦 Almacenamiento", f"{storage} nodos", f"{round(storage/total*100)}%")
        col2.metric("🔋 Recarga", f"{recharge} nodos", f"{round(recharge/total*100)}%")
        col3.metric("👤 Clientes", f"{client} nodos", f"{round(client/total*100)}%")

        st.session_state.simulation = sim

# ----------------- Pestaña 1: Explorar red ------------------

# Sección para visualizar y explorar rutas
with tabs[1]:
    st.markdown("## 🌍 Exploración de Red y Rutas")
    st.markdown("Visualiza los nodos y selecciona una ruta para destacar.")

    if "entrega_completada" not in st.session_state:
        st.session_state.entrega_completada = False

    # Dibuja el grafo con nodos y ruta si hay
    def draw_graph(sim, path=None):
        graph = sim.get_graph()
        roles = sim.get_roles()
        G = nx.Graph()
        pos = {}
        color_map = []

        for v in graph.vertices():
            label = str(v)
            pos[label] = (hash(v) % 100, hash(label[::-1]) % 100)
            role = roles[v]

            if "Cliente" in role:
                color_map.append("blue")
            elif "Almacenamiento" in role:
                color_map.append("orange")
            elif "Recarga" in role:
                color_map.append("green")
            else:
                color_map.append("gray")

            G.add_node(label)

        for edge in graph.edges():
            u, v = edge.endpoints()
            G.add_edge(str(u), str(v), weight=edge.element())

        edge_colors = [
            "red" if path and ((u, v) in path or (v, u) in path) else "gray"
            for u, v in G.edges()
        ]

        fig, ax = plt.subplots(figsize=(10, 6))
        nx.draw(G, pos, with_labels=True, node_color=color_map,
                edge_color=edge_colors, node_size=700, font_size=10, ax=ax)

        try:
            edge_labels = nx.get_edge_attributes(G, 'weight')
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax)
        except Exception as e:
            st.warning(f"No se pudieron mostrar etiquetas de aristas: {e}")

        legend_handles = [
            mpatches.Patch(color='blue', label='Cliente'),
            mpatches.Patch(color='orange', label='Almacenamiento'),
            mpatches.Patch(color='green', label='Recarga')
        ]
        ax.legend(handles=legend_handles, title="Tipo de Nodo", loc="best")
        st.pyplot(fig)

    if "simulation" in st.session_state:
        sim = st.session_state.simulation
        vertices = list(sim.get_graph().vertices())
        labels = [str(v) for v in vertices]
        label_to_vertex = {str(v): v for v in vertices}

        # Selección de origen y destino para buscar ruta
        col1, col2 = st.columns(2)
        with col1:
            origen = st.selectbox("📍 Origen", labels)
        with col2:
            destino = st.selectbox("🎯 Destino", labels)

        if st.button("✈ Calcular Ruta"):
            if origen == destino:
                st.warning("⚠️ El nodo origen y destino no pueden ser iguales.")
            else:
                path, cost = sim.find_route(label_to_vertex[origen], label_to_vertex[destino])
                if path and cost is not None:
                    st.session_state["ruta_actual"] = {
                        "path": path,
                        "cost": cost,
                        "origen": origen,
                        "destino": destino
                    }
                    st.session_state.entrega_completada = False  # ← Reiniciar bandera al calcular nueva ruta
                    st.success(f"✅ Ruta: {' → '.join(str(v) for v in path)} | Costo total: {cost}")
                    draw_graph(sim, [(str(u), str(v)) for u, v in zip(path, path[1:])])
                else:
                    st.warning("⚠️ No se encontró una ruta válida entre los nodos seleccionados.")

        ruta_actual = st.session_state.get("ruta_actual")
        entregado = st.session_state.get("entrega_completada", False)

        if not ruta_actual:
            draw_graph(sim)

        # Verifica si ya existe la ruta actual y permite registrar la orden
        elif ruta_actual and not entregado:
            if st.button("✅ Complete Delivery and Create Order"):
                path = ruta_actual["path"]
                cost = ruta_actual["cost"]
                origen = ruta_actual["origen"]
                destino = ruta_actual["destino"]

                destino_vertex = label_to_vertex[destino]
                client_id = str(destino_vertex)
                if client_id not in sim.clients:
                    sim.clients[client_id] = Client(client_id, f"Cliente {client_id}", destino_vertex)
                client = sim.clients[client_id]
                client.register_order()

                orden_existente = None
                for o in sim.orders:
                    if (
                        o.client.id == client.id and
                        str(o.origin) == origen and
                        str(o.destination) == destino and
                        o.status == "Pendiente"
                    ):
                        orden_existente = o
                        break

                if orden_existente:
                    orden_existente.status = "Entregado"
                    orden_existente.delivered_at = datetime.now()
                    orden_existente.path = path
                    orden_existente.cost = cost
                    order = orden_existente  # ← Aquí se asegura la variable "order"
                else:
                    order = Order(
                        client=client,
                        origin=label_to_vertex[origen],
                        destination=destino_vertex,
                        path=path,
                        cost=cost
                    )
                    order.status = "Entregado"
                    order.delivered_at = datetime.now()
                    sim.orders.append(order)
                sim.route_log.append(path)
                st.session_state.simulation = sim

                st.session_state["entrega_completada"] = True
                st.session_state["ruta_actual"] = None

                st.success(f"📦 Orden entregada exitosamente Cliente: {client.name} | ID: {client.id} Fecha: {order.delivered_at.strftime('%Y-%m-%d %H:%M:%S')}")
                draw_graph(sim)

        elif ruta_actual and entregado:
            draw_graph(sim)
    else:
        st.info("ℹ️ Primero ejecuta una simulación en la pestaña 1.")

# ----------------- Pestaña 2: Clientes y Órdenes ------------------

# Muestra información de clientes y pedidos
with tabs[2]:
    st.markdown("## 🌐 Clientes y Órdenes Generadas")
    if "simulation" not in st.session_state:
        st.warning("⚠️ Primero ejecuta una simulación.")
    else:
        sim = st.session_state.simulation
        clients = sim.get_clients()
        orders = sim.get_all_orders()

        # Lista de clientes registrados en la simulación
        st.subheader("👤 Lista de Clientes")
        clients_data = [
            {
                "ID": client.id,
                "Nombre": client.name,
                "Ubicación": str(client.vertex),
                "Total Pedidos": client.total_orders
            } for client in clients
        ]
        for client in clients_data:
            st.json(json.dumps({
                "client_id": client["ID"],
                "name": client["Nombre"],
                "type": "premium",
                "total_orders": client["Total Pedidos"]
            }))

        # Lista de órdenes realizadas en el sistema
        st.subheader("📦 Lista de Órdenes")
        orders_data = [
            {
                "ID": order.id,
                "Cliente": order.client.name,
                "Origen": str(order.origin),
                "Destino": str(order.destination),
                "Costo": order.cost
            } for order in orders
        ]
        
        for order in orders:
            st.json(json.dumps({
                "order_id": order.id,
                "client": order.client.name,
                "client_id": order.client.id,
                "origin": str(order.origin),
                "destination": str(order.destination),
                "status": order.status,
                "priority": order.priority,
                "created_at": order.created_at.isoformat(),
                "delivered_at": order.delivered_at.isoformat() if order.delivered_at else None,
                "route_cost": order.cost,
            }))

# ----------------- Pestaña 3: Análisis de rutas ------------------

# Muestra rutas más frecuentes usando AVL
with tabs[3]:
    st.markdown("## 📋 Análisis de Rutas Frecuentes")
    if "simulation" not in st.session_state:
        st.warning("⚠️ Ejecuta una simulación primero.")
    else:
        sim = st.session_state.simulation
        route_log = sim.route_log

        if not route_log:
            st.info("ℹ️ No hay rutas registradas todavía.")
        else:
            # Inserta rutas en un árbol AVL
            avl = AVLTree()
            for path in route_log:
                route = Route(path)
                avl.insert(route, route)

            rutas_ordenadas = avl.get_in_order()
            st.subheader("📝 Rutas (ordenadas por frecuencia/costo)")
            for ruta, obj in rutas_ordenadas:
                st.code(ruta.to_label())

            # Visualiza rutas en orden y diagrama AVL
            st.subheader("🌳 Visualización del Árbol AVL")
            vis = AVLVisualizer()
            fig = vis.draw(avl.root)
            st.pyplot(fig)

# ----------------- Pestaña 4: Estadísticas ------------------

# Pestaña de estadísticas generales
with tabs[4]:
    st.markdown("## 📈 Estadísticas Generales del Sistema")
    
    # Función auxiliar para graficar barras
    def interaccion_grafico(titulo, etiquetas, valores):
        df = pd.DataFrame({'Nodo': etiquetas, 'Visitas': valores})
        fig = px.bar(df, x='Nodo', y='Visitas', title=titulo,
                    color_discrete_sequence=['skyblue'])
        fig.update_traces(hovertemplate='Nodo: %{x}<br>Visitas: %{y}<extra></extra>')
        st.plotly_chart(fig, use_container_width=True)

    if "simulation" not in st.session_state:
        st.warning("⚠️ Ejecuta una simulación primero.")
    else:
        sim = st.session_state.simulation
        route_log = sim.route_log
        roles = sim.get_roles()

        # Conteo de visitas por tipo de nodo
        visit_counter = Counter()
        for path in route_log:
            for node in path:
                role = roles.get(node, "Desconocido")
                visit_counter[(str(node), role)] += 1

        tipo_visitas = {"Cliente": [], "Almacenamiento": [], "Recarga": []}
        for (node, role), count in visit_counter.items():
            for tipo in tipo_visitas:
                if tipo in role:
                    tipo_visitas[tipo].append((node, count))

        st.subheader("📊 Frecuencia de visitas por tipo de nodo")

        col1, col2, col3 = st.columns(3)

        for tipo, col in zip(["Cliente", "Recarga", "Almacenamiento"], [col1, col2, col3]):
            datos = tipo_visitas[tipo]
            if datos:
                etiquetas, valores = zip(*datos)
                with col:
                    interaccion_grafico(f"{tipo}s Más Visitados", etiquetas, valores)
            else:
                col.info(f"No hay visitas registradas para {tipo.lower()}s.")

        st.subheader("🥧 Proporción de Tipos de Nodos en la Red")
        tipo_counts = Counter(roles.values())

        etiquetas = list(tipo_counts.keys())
        colores = []
        for tipo in etiquetas:
            if "Cliente" in tipo:
                colores.append("blue")
            elif "Almacenamiento" in tipo:
                colores.append("orange")
            elif "Recarga" in tipo:
                colores.append("green")
            else:
                colores.append("gray")

        # Gráfico de pastel con proporción de tipos de nodo
        fig_pie, ax_pie = plt.subplots()
        ax_pie.pie(tipo_counts.values(), labels=etiquetas, autopct="%1.1f%%", colors=colores)
        ax_pie.axis("equal")
        st.pyplot(fig_pie)
