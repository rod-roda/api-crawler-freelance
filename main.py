from fastapi import FastAPI
from controllers.freelance_controller import router as freelance_router

app = FastAPI()

app.include_router(freelance_router)
