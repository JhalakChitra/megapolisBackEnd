from fastapi.middleware.cors import CORSMiddleware

def add_cors(app):
    origins = [
    "http://localhost:5173",  # React dev server

    ]  # your frontend URL

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
