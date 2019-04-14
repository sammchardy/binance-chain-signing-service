import os
import logging

import yaml
from fastapi import FastAPI
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from starlette.middleware.cors import CORSMiddleware

from config.config import ServiceConfig
from api.api import api_router

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)


app = FastAPI(openapi_url="/api/openapi.json")
config: ServiceConfig()


@app.on_event("startup")
async def startup_event():
    global config
    # load config
    with open('../config/config.yml', 'r') as ymlfile:
        config_yml = yaml.load(ymlfile, Loader=yaml.FullLoader)

    # convert settings to pydantic BaseSettings
    ServiceConfig.initialise_config(config=config_yml)

    logging.info("Signing Service Initialised and started up")


app.add_middleware(ProxyHeadersMiddleware)


@app.get("/")
def read_root():
    return {}


# CORS
origins = []

# Set all CORS enabled origins
if os.getenv("BACKEND_CORS_ORIGINS", None):
    origins_raw = os.getenv("BACKEND_CORS_ORIGINS", '').split(",")
    for origin in origins_raw:
        use_origin = origin.strip()
        origins.append(use_origin)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    ),

app.include_router(api_router, prefix='/api')
