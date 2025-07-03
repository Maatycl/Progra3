from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import datetime

def generate_report_pdf(sim):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Informe_{timestamp}.pdf"

    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Título
    elements.append(Paragraph("📄 Informe del Sistema Logístico Autónomo", styles['Title']))
    elements.append(Spacer(1, 12))

    # Tabla de órdenes
    orders_data = [["ID", "Cliente", "Origen", "Destino", "Estado", "Costo"]]
    for order in sim.get_all_orders():
        orders_data.append([
            order.id, order.client.name, str(order.origin),
            str(order.destination), order.status, f"{order.cost:.2f}"
        ])
    elements.append(Paragraph("📦 Órdenes Registradas:", styles['Heading2']))
    t_orders = Table(orders_data)
    t_orders.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
        ("GRID", (0,0), (-1,-1), 1, colors.black)
    ]))
    elements.append(t_orders)
    elements.append(Spacer(1, 20))

    # Tabla de clientes
    clients_data = [["ID", "Nombre", "Total Pedidos"]]
    for client in sim.get_clients():
        clients_data.append([client.id, client.name, client.total_orders])
    elements.append(Paragraph("👤 Clientes Registrados:", styles['Heading2']))
    t_clients = Table(clients_data)
    t_clients.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
        ("GRID", (0,0), (-1,-1), 1, colors.black)
    ]))
    elements.append(t_clients)

    doc.build(elements)
    return filename
