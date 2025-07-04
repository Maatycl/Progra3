import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import matplotlib.pyplot as plt

def generate_report_pdf(sim):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Informe_{timestamp}.pdf"

    doc = SimpleDocTemplate(filename, pagesize=letter)
    doc.title = f"Reporte de Simulación - {timestamp}"

    elements = []
    styles = getSampleStyleSheet()

    # Estilo personalizado para el título principal
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=20,
        textColor=colors.black,
        alignment=1,
        spaceAfter=20,
    )

    # Título principal
    elements.append(Paragraph("Reporte de Simulación", title_style))
    elements.append(HRFlowable(width="100%", color=colors.grey, thickness=1))
    elements.append(Spacer(1, 12))

    # Tabla de Clientes
    elements.append(Paragraph("Clientes Registrados:", styles['Heading2']))
    clients_data = [["Client ID", "Nombre", "Tipo", "Total Órdenes"]]
    for client in sim.get_clients():
        clients_data.append([client.id, client.name, client.type, client.total_orders])
    t_clients = Table(clients_data, repeatRows=1)
    t_clients.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#b6b0b0")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("BACKGROUND", (0,1), (-1,-1), colors.whitesmoke),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, colors.lightgrey]),
        ("FONTSIZE", (0,0), (-1,-1), 9),
    ]))
    elements.append(t_clients)
    elements.append(Spacer(1, 20))

    # Tabla de Órdenes
    elements.append(Paragraph("Órdenes Registradas:", styles['Heading2']))
    for i, order in enumerate(sim.get_all_orders(), start=1):
        elements.append(Paragraph(f"Orden #{i}", styles['Heading3']))
        details = [
            ["Order ID:", order.id],
            ["Cliente:", order.client.name],
            ["Client ID:", order.client.id],
            ["Origen:", order.origin],
            ["Destino:", order.destination],
            ["Estado:", order.status],
            ["Prioridad:", order.priority],
            ["Creada:", str(order.created_at)],
            ["Entregada:", str(order.delivered_at)],
            ["Costo de Ruta:", order.cost],
        ]
        t_order = Table(details, hAlign='LEFT', colWidths=[100, 300])
        t_order.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#C7C7C7")),
            ("GRID", (0,0), (-1,-1), 0.3, colors.grey),
            ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
            ("FONTSIZE", (0,0), (-1,-1), 9),
        ]))
        elements.append(t_order)
        elements.append(Spacer(1, 15))
        elements.append(HRFlowable(width="80%", color=colors.lightgrey, thickness=0.5))
        elements.append(Spacer(1, 10))

    # Gráfico de Distribución de Nodos (Pie chart)
    node_distribution = sim.get_node_distribution()
    node_labels = list(node_distribution.keys())
    node_sizes = list(node_distribution.values())
    colors_pie = ["#5DADE2", "#F5B041", "#58D68D"]

    plt.figure(figsize=(5,5))
    plt.pie(node_sizes, labels=node_labels, autopct='%1.1f%%', startangle=90, colors=colors_pie)
    plt.axis('equal')
    plt.title("Distribución de Nodos", fontsize=12, fontweight="bold")
    pie_img = f"node_distribution_{timestamp}.png"
    plt.savefig(pie_img, bbox_inches='tight')
    plt.close()
    elements.append(Image(pie_img, width=300, height=300))
    elements.append(Spacer(1, 20))

    # Gráfico combinado de Top Visited
    elements.append(Paragraph("Gráficos de Visitas:", styles['Heading2']))
    fig, axes = plt.subplots(1, 3, figsize=(12,4))

    # Clientes más visitados
    top_clients = sim.get_top_visited_clients()
    if top_clients:
        clients_x = [str(c[0]) for c in top_clients]
        clients_y = [c[1] for c in top_clients]
        axes[0].bar(clients_x, clients_y, color="#7EC8E3")
    axes[0].set_title("Clientes Más Visitados", fontsize=10, fontweight="bold")
    axes[0].set_ylabel("Visitas")
    axes[0].set_xlabel("Nodo")

    # Recargas más visitadas
    top_recharges = sim.get_top_visited_recharges()
    if top_recharges:
        recharges_x = [str(r[0]) for r in top_recharges]
        recharges_y = [r[1] for r in top_recharges]
        axes[1].bar(recharges_x, recharges_y, color="#7EC8E3")
    axes[1].set_title("Recargas Más Visitadas", fontsize=10, fontweight="bold")
    axes[1].set_xlabel("Nodo")

    # Almacenes más visitados
    top_storages = sim.get_top_visited_storage_nodes()
    if top_storages:
        storages_x = [str(n[0]) for n in top_storages]
        storages_y = [n[1] for n in top_storages]
        axes[2].bar(storages_x, storages_y, color="#7EC8E3")
    axes[2].set_title("Almacenamientos Más Visitados", fontsize=10, fontweight="bold")
    axes[2].set_xlabel("Nodo")

    plt.tight_layout()
    combined_img = f"top_visited_combined_{timestamp}.png"
    plt.savefig(combined_img, bbox_inches='tight')
    plt.close()
    elements.append(Image(combined_img, width=500, height=200))

    doc.build(elements)
    return filename