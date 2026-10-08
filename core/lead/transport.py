from time import sleep
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
import httpx
from network.connection import request
from conf import config

net_config = config["network"]
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
RETRY_STATUS = {429, 502, 503, 504}
MAX_ATTEMPTS = net_config["max_attempts"]
TIMEOUT = net_config["connect"], net_config["read"]

def _retry_delay(response, attempt):
    delay = 10 * (attempt + 1)
    value = response.headers.get("Retry-After", "").strip()
    if value.isdigit():
        return max(delay, int(value))
    if value:
        try:
            date = parsedate_to_datetime(value)
            if date.tzinfo is None:
                date = date.replace(tzinfo=timezone.utc)
            delay = max(delay, (date - datetime.now(timezone.utc)).total_seconds())
        except (TypeError, ValueError, OverflowError):
            pass
    return delay

def _parse_response(response):
    if not response.is_success:
        raise RuntimeError(f"Overpass HTTP {response.status_code}\nResposta: {response.text[:2000]}")
    try:
        payload = response.json()
    except ValueError as exc:
        raise RuntimeError("Overpass retornou uma resposta que não é JSON") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("Resposta inesperada da Overpass")
    if payload.get("remark"):
        raise RuntimeError(f"Overpass: {payload['remark']}")
    elements = payload.get("elements")
    if not isinstance(elements, list):
        raise RuntimeError("Resposta sem lista válida de elementos")
    return elements

def _request_overpass(query):
    for attempt in range(MAX_ATTEMPTS):
        try:
            response = request(
                method="POST",
                url=OVERPASS_URL,
                data={"data": query},
                headers={
                    "Accept": "application/json",
                    "User-Agent": "TRCP/0.1",
                },
                timeout=TIMEOUT,
                retries=1,
            )
        except httpx.HTTPStatusError as exc:
            response = exc.response
        except httpx.RequestError:
            if attempt == MAX_ATTEMPTS - 1:
                raise
            sleep(10 * (attempt + 1))
            continue

        try:
            if response.status_code in RETRY_STATUS and attempt < MAX_ATTEMPTS - 1:
                delay = _retry_delay(response, attempt)
            else:
                return _parse_response(response)
        finally:
            response.close()
        sleep(delay)
    raise RuntimeError("Não foi possível consultar a Overpass")

