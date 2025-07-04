from fastapi import FastAPI
<<<<<<< HEAD
from api.controllers import client_routes, order_routes, report_routes
#info_routes,  
=======
from api.controllers import client_routes, order_routes, info_routes, report_routes 
>>>>>>> 561af5b8b8207df4be1a3e2593168893dade1e5c

app = FastAPI()

app.include_router(client_routes.router)
<<<<<<< HEAD
#app.include_router(info_routes.router)
app.include_router(order_routes.router)
app.include_router(report_routes.router)  # ¡Agrega esto!
=======
app.include_router(order_routes.router)
app.include_router(info_routes.router)
app.include_router(report_routes.router)
>>>>>>> 561af5b8b8207df4be1a3e2593168893dade1e5c
