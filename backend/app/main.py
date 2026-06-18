
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api import api_router
from app.mqtt_client import start_mqtt, stop_mqtt


@asynccontextmanager
async def lifespan(app: FastAPI):
    await start_mqtt()
    yield
    stop_mqtt()


app = FastAPI(
    title="SmartParkU - Backend",
    description="API de autenticación, sensores IoT y control de acceso para SmartParkU UCC",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

