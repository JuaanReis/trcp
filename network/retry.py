from time import sleep
from conf import config

network_config = config.get("network", {})

def backoff_delay(attempt: int, base_delay: float = network_config.get("timeout", 6.0)) -> None:
    sleep(base_delay * (2 ** attempt))

def should_retry(status_code: int) -> bool:
    return status_code in {429, 500, 502, 503, 504}

def get_retry_after(headers: dict, default: float = network_config.get("retry_after", 1.0)) -> float:
    return float(headers.get("Retry-After", default))