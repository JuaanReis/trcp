from pathlib import Path
from dataclasses import dataclass
from os import environ
from functools import lru_cache
from dotenv import load_dotenv

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  

try:
    _CONFIG_PATH = Path(__file__).parent / "config.toml"  
    with _CONFIG_PATH.open("rb") as f:
        config = tomllib.load(f)

    if not config:
        raise RuntimeError("config.toml is empty")

except FileNotFoundError:
    raise FileNotFoundError(f"TOML configuration file not found in {_CONFIG_PATH}")

except tomllib.TOMLDecodeError:
    raise RuntimeError(f"Error parsing the config.toml file {_CONFIG_PATH}")

@dataclass(frozen=True)
class Settings:
    google_api_key: str

@lru_cache
def get_settings() -> Settings:
    load_dotenv()

    return Settings(
        google_api_key = environ["GOOGLE_API_KEY"],
    )