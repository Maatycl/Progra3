from fastapi import FastAPI
from api.controllers import client_routes, report_routes
#info_routes, order_routes, 

app = FastAPI()

app.include_router(client_routes.router)
#app.include_router(info_routes.router)
#app.include_router(order_routes.router)
app.include_router(report_routes.router)  # ¡Agrega esto!
