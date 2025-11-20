from fastapi import FastAPI
from app.database import Base, engine
from app.routes import auth_routes, org_routes

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Megapolis Backend API",
    version="1.0"
)

app.include_router(auth_routes.router)
app.include_router(org_routes.router)
