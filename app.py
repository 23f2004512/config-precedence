from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from typing import List
import yaml
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

DEFAULTS = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}


def to_bool(value):
    return str(value).lower() in ("true", "1", "yes", "on")


@app.get("/effective-config")
def effective_config(set: List[str] = Query(default=[])):
    # 1. Start with defaults
    config = DEFAULTS.copy()

    # 2. YAML
    with open("config.development.yaml") as f:
        yaml_config = yaml.safe_load(f) or {}
    config.update(yaml_config)

    # 3. .env layer
    env_layer = {}

    if os.getenv("NUM_WORKERS") is not None:
        env_layer["workers"] = os.getenv("NUM_WORKERS")

    if os.getenv("APP_DEBUG") is not None:
        env_layer["debug"] = os.getenv("APP_DEBUG")

    if os.getenv("APP_API_KEY") is not None:
        env_layer["api_key"] = os.getenv("APP_API_KEY")

    config.update(env_layer)

    # 4. OS environment variables (APP_* prefix)
    os_layer = {}

    if os.getenv("APP_PORT") is not None:
        os_layer["port"] = os.getenv("APP_PORT")

    if os.getenv("APP_WORKERS") is not None:
        os_layer["workers"] = os.getenv("APP_WORKERS")

    if os.getenv("APP_LOG_LEVEL") is not None:
        os_layer["log_level"] = os.getenv("APP_LOG_LEVEL")

    if os.getenv("APP_DEBUG") is not None:
        os_layer["debug"] = os.getenv("APP_DEBUG")

    if os.getenv("APP_API_KEY") is not None:
        os_layer["api_key"] = os.getenv("APP_API_KEY")

    config.update(os_layer)

    # 5. CLI overrides (?set=key=value)
    for item in set:
        if "=" in item:
            key, value = item.split("=", 1)
            config[key] = value

    # 6. Type coercion
    config["port"] = int(config["port"])
    config["workers"] = int(config["workers"])
    config["debug"] = to_bool(config["debug"])
    config["log_level"] = str(config["log_level"])

    # 7. Mask secret
    config["api_key"] = "****"

    return config