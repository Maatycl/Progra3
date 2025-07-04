import sys 
import os
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import plotly.express as px
import json
from collections import Counter
from datetime import datetime
from sim.simulation import Simulation
from visual.map.map_builder import draw_folium_map
from visual.avl_visualizer import AVLVisualizer
from domain.route import Route
from tda.avl import AVLTree
from domain.order import Order
from domain.client import Client
from visual.report_generator import generate_report_pdf
from api.global_simulation import set as set_simulation
import threading
import uvicorn

def run_api():
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=False)

threading.Thread(target=run_api, daemon=True).start()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configura título y diseño ancho para la app
st.set_page_config(page_title="Sistema Logístico Autónomo", layout="wide")

tabs = st.tabs([
    "🔄 Run Simulation",
    "🌍 Explore Network",
    "🌐 Clients & Orders",
    "📋 Route Analytics",
    "📈 General Statistics"
])

# ----------------- Pestaña 0: Run Simulation ------------------
with tabs[0]:
    st.markdown("## 🔄 Simulación de Red Logística")
    st.markdown("Ajusta los parámetros y ejecuta la simulación para generar la red.")

    col1, col2, col3 = st.columns(3)
    with col1:
        n_nodes = st.slider("🔢 Número de nodos", 10, 150, 15)
    with col2:
        m_edges = st.slider("🔗 Número de aristas", 10, 300, 20)
    with col3:
        n_orders = st.slider("📦 Número de órdenes", 10, 500, 10)

    st.divider()
    st.markdown("### 📊 Proporción de Roles (automática)")
    st.markdown("- 📦 **Almacenamiento**: 20%")
    st.markdown("- 🔋 **Recarga**: 20%")
    st.markdown("- 👤 **Clientes**: 60%")

    st.divider()
    if st.button("🚀 Iniciar Simulación", use_container_width=True):
        
        if "coords" in st.session_state:
            del st.session_state["coords"]

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
        set_simulation(sim)
        st.session_state.ruta_actual = None
        st.session_state.mst_actual = None
        st.session_state.info_ruta = None

# ----------------- Pestaña 1: Explore Network ------------------
with tabs[1]:
    st.markdown("## 🌍 Exploración de Red y Rutas")
    st.markdown("Visualiza los nodos y selecciona una ruta para destacar sobre el mapa.")

    if "entrega_completada" not in st.session_state:
        st.session_state.entrega_completada = False

    if "simulation" in st.session_state:
        sim = st.session_state.simulation
        graph = sim.get_graph()
        vertices = list(graph.vertices())
        labels = [str(v) for v in vertices]
        label_to_vertex = {str(v): v for v in vertices}

        col1, col2 = st.columns(2)
        with col1:
            origen = st.selectbox("📍 Origen", labels)
        with col2:
            destino = st.selectbox("🎯 Destino", labels)

        st.markdown("### 🔍 Algoritmo de Enrutamiento")
        algorithm = st.radio("Algoritmo", options=["Dijkstra"], index=0)

        if st.button("✈ Calcular ruta", use_container_width=True):
            if origen == destino:
                st.warning("⚠️ El nodo origen y destino no pueden ser iguales.")
            else:
                adjusted_path, adjusted_cost = sim.find_route(label_to_vertex[origen], label_to_vertex[destino])
                if adjusted_path:
                    st.session_state["ruta_actual"] = {"path": adjusted_path, "cost": adjusted_cost}
                    st.session_state["mst_actual"] = None  # limpiar MST
                    st.success("✅ Ruta calculada correctamente con Dijkstra y autonomía.")
                    st.session_state["info_ruta"] = {
                        "nodos": ' → '.join(str(v) for v in adjusted_path),
                        "costo": adjusted_cost
                    }
                else:
                    st.session_state["ruta_actual"] = None
                    st.session_state["info_ruta"] = None
                    st.warning("⚠️ No se encontró ninguna ruta posible considerando autonomía y recargas.")


        if st.button("🌲 Mostrar MST", use_container_width=True):
            mst_edges = sim.compute_mst()
            if mst_edges:
                st.session_state["mst_actual"] = mst_edges
                st.session_state["ruta_actual"] = None  # limpiar ruta
                st.session_state["info_ruta"] = None
                st.success("🌲 MST generado y mostrado correctamente.")
            else:
                st.session_state["mst_actual"] = None
                st.session_state["info_ruta"] = None
                st.warning("⚠️ No se pudo generar el MST.")

            # Botón adicional para ocultar el MST
        if st.button("❌ Ocultar MST", use_container_width=True):
            st.session_state["mst_actual"] = None
            st.success("🚫 MST oculto correctamente.")

        # ✅ ÚNICA llamada al mapa al final, actualiza con ruta/MST si existen
        path = st.session_state["ruta_actual"]["path"] if st.session_state.get("ruta_actual") else None
        mst = st.session_state["mst_actual"] if st.session_state.get("mst_actual") else None
        draw_folium_map(sim, path=path, mst=mst)

        # Mostrar info de la ruta debajo del mapa
        if st.session_state.get("info_ruta"):
            st.markdown("---")
            st.markdown(f"**Nodos en la ruta:** {st.session_state['info_ruta']['nodos']}")
            st.markdown(f"**Costo total:** {st.session_state['info_ruta']['costo']}")
            # Botón para completar la ruta
            if st.button("✅ Completar Ruta", use_container_width=True):
                sim = st.session_state.simulation
                # Encuentra la orden que coincide con el origen y destino actuales
                for order in sim.get_all_orders():
                    if str(order.origin) == origen and str(order.destination) == destino:
                        order.status = "Entregado"
                        order.delivered_at = datetime.now()
                        st.success(f"Orden {order.id} marcada como entregada.")
                        break
                else:
                    st.warning("⚠️ No se encontró una orden que coincida con el origen y destino seleccionados.")

        # Mostrar cantidad de nodos por tipo debajo del mapa
        roles = sim.get_roles()
        storage = sum(1 for r in roles.values() if "Almacenamiento" in r)
        recharge = sum(1 for r in roles.values() if "Recarga" in r)
        client = sum(1 for r in roles.values() if "Cliente" in r)
        st.markdown("---")
        st.markdown(f"**Nodos:**  ")
        st.markdown(f"- 📦 Almacenamiento: {storage}")
        st.markdown(f"- 🔋 Recarga: {recharge}")
        st.markdown(f"- 👤 Clientes: {client}")

    else:
        st.info("ℹ️ Primero ejecuta una simulación en la pestaña 1.")



# ----------------- Pestaña 2: Clients & Orders ------------------

with tabs[2]:
    st.markdown("## 🌐 Clientes y Órdenes Generadas")
    if "simulation" not in st.session_state:
        st.warning("⚠️ Primero ejecuta una simulación en la pestaña 1.")
    else:
        sim = st.session_state.simulation
        clients = sim.get_clients()
        orders = sim.get_all_orders()

        # Lista de clientes registrados en la simulación
        st.subheader("👤 Clientes")
        if clients:
            clients_json = []
            for client in clients:
                client_info = {
                    "client_id": client.id,
                    "name": client.name,
                    "type": "normal" if client.total_orders < 5 else "premium",
                    "total_orders": client.total_orders
                }
                clients_json.append(client_info)
            st.json(clients_json)
        else:
            st.info("ℹ️ No hay clientes registrados todavía.")

        # Lista de órdenes realizadas en el sistema
        st.subheader("📦 Orders")
        if orders:
            orders_json = []
            for order in orders:
                order_info = {
                    "order_id": str(order.id),
                    "client": order.client.name,
                    "client_id": order.client.id,
                    "origin": str(order.origin),
                    "destination": str(order.destination),
                    "status": order.status,
                    "priority": order.priority,
                    "created_at": order.created_at.isoformat(),
                    "delivered_at": order.delivered_at.isoformat() if order.delivered_at else None,
                    "route_cost": order.cost,
                }
                orders_json.append(order_info)
            st.json(orders_json)
        else:
            st.info("ℹ️ No hay órdenes registradas todavía.")

# ----------------- Pestaña 3: Analisis de Rutas ------------------

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

            # Botón para generar informe PDF
            st.subheader("📄 Generar Informe PDF")
            if st.button("📝 Generar PDF del Informe", use_container_width=True):
                filename = generate_report_pdf(sim)
                st.success(f"✅ Informe generado: {filename}")
                with open(filename, "rb") as pdf_file:
                    st.download_button(
                        label="⬇️ Descargar Informe PDF",
                        data=pdf_file,
                        file_name=filename,
                        mime="application/pdf",
                        use_container_width=True
                    )


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
