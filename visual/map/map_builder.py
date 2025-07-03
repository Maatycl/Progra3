import folium
from streamlit_folium import st_folium
import numpy as np

def draw_folium_map(sim, path=None, mst=None):
    # Centra el mapa en Temuco (o donde prefieras)
    m = folium.Map(location=[-38.7359, -72.5904], zoom_start=13)
    
    graph = sim.get_graph()
    roles = sim.get_roles()
    vertices = list(graph.vertices())

    # Generar coordenadas reproducibles en círculo
    coords = {}
    for i, v in enumerate(vertices):
        angle = i * 2 * np.pi / len(vertices)
        lat = -38.7359 + 0.01 * np.sin(angle)
        lon = -72.5904 + 0.01 * np.cos(angle)
        coords[v] = [lat, lon]

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
            location=coords[v],
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
            locations=[coords[u], coords[v]],
            color="gray",
            weight=2,
            opacity=0.5
        ).add_to(m)
    
    # Dibuja la ruta calculada, si se pasa
    if path:
        route_coords = [coords[node] for node in path]
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
                locations=[coords[u], coords[v]],
                color="purple",
                weight=3,
                dash_array="5, 5",
                opacity=0.7,
                popup="🌲 Arista MST"
            ).add_to(m)

    # Muestra el mapa en Streamlit
    st_folium(m, use_container_width=True)
