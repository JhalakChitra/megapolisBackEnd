from fastapi import FastAPI
from app.routes import auth_routes, org_routes, user_routes
from app.database import Base, engine

# create DB tables (for development; use alembic in production)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Megapolis Backend API")

app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
app.include_router(org_routes.router, prefix="/org", tags=["Organization"])
app.include_router(user_routes.router, prefix="/users", tags=["Users"])

@app.get("/")
def root():
    return {"message": "Megapolis Backend Running"}
