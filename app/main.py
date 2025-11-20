from fastapi import FastAPI
from app.database import Base, engine
from app.routes import auth_routes, org_routes
from app.middleware.cors import add_cors  # import CORS middleware

# Create tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Megapolis Backend API",
    version="1.0"
)

# Add CORS middleware
add_cors(app)

# Include routers
app.include_router(auth_routes.router)
app.include_router(org_routes.router)
