import folium
from streamlit_folium import st_folium
import numpy as np
import streamlit as st

def draw_folium_map(sim, path=None, mst=None):
    # Centra el mapa en Temuco (o donde prefieras)
    m = folium.Map(location=[-38.7359, -72.5904], zoom_start=13)
    
    graph = sim.get_graph()
    roles = sim.get_roles()
    vertices = list(graph.vertices())

    if "coords" not in st.session_state:
        coords = {}
        for v in vertices:
            lat = -38.7359 + np.random.uniform(-0.02, 0.02)
            lon = -72.5904 + np.random.uniform(-0.02, 0.02)
            coords[str(v)] = [lat, lon]
        st.session_state.coords = coords
    else:
        coords = st.session_state.coords

    # Agrega nodos al mapa con colores según rol
    for v in vertices:
        role = roles[v]
        color = "gray"
        if "Cliente" in role:
            color = "blue"
        elif "Almacenamiento" in role:
            color = "orange"
        elif "Recarga" in role:
            color = "green"
        
        folium.CircleMarker(
            location=coords[str(v)],
            radius=7,
            color=color,
            fill=True,
            fill_color=color,
            popup=f"🟢 Nodo: {v}<br>Rol: {role}"
        ).add_to(m)
    
    # Agrega aristas del grafo
    for edge in graph.edges():
        u, v = edge.endpoints()
        folium.PolyLine(
            locations=[coords[str(u)], coords[str(v)]],
            color="gray",
            weight=2,
            opacity=0.5
        ).add_to(m)
    
    # Dibuja la ruta calculada, si se pasa
    if path:
        route_coords = [coords[str(node)] for node in path]
        folium.PolyLine(
            locations=route_coords,
            color="red",
            weight=4,
            opacity=0.8,
            popup="🚚 Ruta Calculada"
        ).add_to(m)

    # Dibuja el MST, si se pasa
    if mst:
        for u, v in mst:
            folium.PolyLine(
                locations=[coords[str(u)], coords[str(v)]],
                color="green",
                weight=3,
                dash_array="5, 5",
                opacity=0.7,
                popup="🌲 Arista MST"
            ).add_to(m)

    # Muestra el mapa en Streamlit
    st_folium(m, use_container_width=True)
