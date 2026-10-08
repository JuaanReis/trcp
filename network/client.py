from httpx import Client, Timeout, Limits, request, Response
from network.headers import build_headers
from conf import config

network_config = config.get("network", {})

def _base_limits() -> Limits:
    return Limits(max_keepalive_connections=network_config.get("max_keepalive_connections", 20),
                   max_connections=network_config.get("max_connections", 50))

def make_scan_client(rotate_ua: bool = True) -> Client:
    return Client(
        http2=network_config.get("http2", False),
        verify=network_config.get("verify_ssl", True),
        follow_redirects=network_config.get("follow_redirects", True),
        timeout=Timeout(timeout=network_config.get("timeout", 5.0), 
                        connect=network_config.get("connect", 1.5), 
                        read=network_config.get("read", 3.0)),
        limits=_base_limits(),
        headers=build_headers(rotate_ua=rotate_ua),
    )

client: Client = make_scan_client(network_config.get("rotate_ua", True))