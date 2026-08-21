from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routes import auth_routes, user_routes, file_routes

# just using create_all here to keep setup to one command. I know Alembic
# migrations would be the "proper" way to do this in a real project, but
# felt like overkill for a screening task
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Osdag Login System - Custom Backend")

# needed this so the provided index.html testing client (opened directly in
# a browser, different origin than this API) can actually reach these
# endpoints - without this the browser blocks the requests before they even
# get here
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(file_routes.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "osdag-login-system-custom-backend"}
