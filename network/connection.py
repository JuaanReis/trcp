from time import sleep
import httpx
from network.client import client
from network.retry import backoff_delay, should_retry, get_retry_after

def request(
    method: str,
    url: str,
    params: dict | None = None,
    *,
    data: dict | None = None,
    json: dict | None = None,
    headers: dict | None = None,
    retries: int = 3,
    delay: float = 0.6,
    timeout: float | httpx.Timeout = 5,
    allow_redirects: bool = False,
) -> httpx.Response:
    
    if retries < 1:
        raise ValueError("retries precisa ser positivo")

    if data is not None and json is not None:
        raise ValueError("Use data ou json, não ambos")

    for attempt in range(retries):
        try:
            response = client.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json,
                headers=headers,
                timeout=timeout,
                follow_redirects=allow_redirects,
            )

        except httpx.HTTPStatusError as exc:
            response = exc.response

        except httpx.RequestError:
            if attempt == retries - 1:
                raise

            backoff_delay(attempt, base_delay=delay)
            continue

        if (
            should_retry(response.status_code)
            and attempt < retries - 1
        ):
            try:
                retry_after = get_retry_after(dict(response.headers))
            finally:
                response.close()

            if retry_after is not None and retry_after > 0:
                sleep(retry_after)
            else:
                backoff_delay(attempt, base_delay=delay)

            continue

        return response

    raise RuntimeError("As tentativas de requisição foram esgotadas")