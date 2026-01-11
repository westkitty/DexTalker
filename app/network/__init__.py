"""Network utilities package for DexTalker."""
from .utils import (
    get_local_ip,
    get_tailscale_ip,
    get_magicDNS_hostname,
    is_tailscale_ip,
    is_localhost,
    is_lan_ip,
    generate_shareable_urls,
    check_port_available,
    get_tailscale_status
)
from .auth import (
    NetworkAuth,
    generate_access_token,
    verify_access_token
)

__all__ = [
    'get_local_ip',
    'get_tailscale_ip',
    'get_magicDNS_hostname',
    'is_tailscale_ip',
    'is_localhost',
    'is_lan_ip',
    'generate_shareable_urls',
    'check_port_available',
    'get_tailscale_status',
    'NetworkAuth',
    'generate_access_token',
    'verify_access_token'
]
