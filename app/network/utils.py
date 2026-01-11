"""
Network utilities for DexTalker LAN/Tailnet access.
Handles IP detection, Tailscale integration, and shareable URL generation.
"""
import socket
import subprocess
import json
import logging
from typing import List, Optional, Dict
import ipaddress

logger = logging.getLogger("DexTalker.Network")


def get_local_ip() -> str:
    """
    Get primary LAN IPv4 address.
    
    Returns:
        str: Primary LAN IP or 127.0.0.1 if unavailable
    """
    try:
        # Connect to external DNS to determine which interface to use
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        
        # Verify it's not loopback
        if ip.startswith("127."):
            return "127.0.0.1"
            
        logger.info(f"Detected LAN IP: {ip}")
        return ip
    except Exception as e:
        logger.warning(f"Failed to get LAN IP: {e}")
        return "127.0.0.1"


def get_tailscale_ip() -> Optional[str]:
    """
    Detect Tailscale IPv4 address if available.
    
    Returns:
        Optional[str]: Tailscale IP (100.x.x.x) or None
    """
    try:
        result = subprocess.run(
            ["tailscale", "ip", "-4"],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        if result.returncode == 0:
            ip = result.stdout.strip()
            # Verify it's in Tailscale range
            if ip.startswith("100."):
                logger.info(f"Detected Tailscale IP: {ip}")
                return ip
                
    except FileNotFoundError:
        logger.debug("Tailscale not installed")
    except subprocess.TimeoutExpired:
        logger.warning("Tailscale command timed out")
    except Exception as e:
        logger.debug(f"Tailscale detection failed: {e}")
    
    return None


def get_magicDNS_hostname() -> Optional[str]:
    """
    Get Tailscale MagicDNS hostname if available.
    
    Returns:
        Optional[str]: MagicDNS hostname or None
    """
    try:
        result = subprocess.run(
            ["tailscale", "status", "--json"],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            hostname = data.get("Self", {}).get("DNSName", "").rstrip(".")
            
            if hostname:
                logger.info(f"Detected MagicDNS: {hostname}")
                return hostname
                
    except FileNotFoundError:
        logger.debug("Tailscale not installed")
    except subprocess.TimeoutExpired:
        logger.warning("Tailscale status check timed out")
    except (json.JSONDecodeError, KeyError) as e:
        logger.debug(f"Failed to parse Tailscale status: {e}")
    except Exception as e:
        logger.debug(f"MagicDNS detection failed: {e}")
    
    return None


def is_tailscale_ip(ip: str) -> bool:
    """
    Check if an IP address is in the Tailscale range (100.64.0.0/10).
    
    Args:
        ip: IP address to check
        
    Returns:
        bool: True if IP is in Tailscale range
    """
    try:
        addr = ipaddress.ip_address(ip)
        tailnet = ipaddress.ip_network("100.64.0.0/10")
        return addr in tailnet
    except (ValueError, ipaddress.AddressValueError):
        return False


def is_localhost(ip: str) -> bool:
    """
    Check if an IP is localhost.
    
    Args:
        ip: IP address to check
        
    Returns:
        bool: True if localhost
    """
    return ip in ["127.0.0.1", "::1", "localhost"]


def is_lan_ip(ip: str) -> bool:
    """
    Check if an IP is a private LAN address (RFC1918).
    
    Args:
        ip: IP address to check
        
    Returns:
        bool: True if private LAN IP
    """
    try:
        addr = ipaddress.ip_address(ip)
        
        # Check private ranges
        private_ranges = [
            ipaddress.ip_network("10.0.0.0/8"),
            ipaddress.ip_network("172.16.0.0/12"),
            ipaddress.ip_network("192.168.0.0/16"),
        ]
        
        return any(addr in network for network in private_ranges)
    except (ValueError, ipaddress.AddressValueError):
        return False


def generate_shareable_urls(port: int, protocol: str = "http") -> Dict[str, Optional[str]]:
    """
    Generate all shareable URLs for the current host.
    
    Args:
        port: Server port number
        protocol: URL protocol (http or https)
        
    Returns:
        Dict with keys: localhost, lan, tailscale, magicDNS
    """
    urls = {
        "localhost": f"{protocol}://127.0.0.1:{port}",
        "lan": None,
        "tailscale": None,
        "magicDNS": None
    }
    
    # LAN IP
    lan_ip = get_local_ip()
    if lan_ip != "127.0.0.1":
        urls["lan"] = f"{protocol}://{lan_ip}:{port}"
    
    # Tailscale IP
    ts_ip = get_tailscale_ip()
    if ts_ip:
        urls["tailscale"] = f"{protocol}://{ts_ip}:{port}"
    
    # MagicDNS hostname
    magic = get_magicDNS_hostname()
    if magic:
        urls["magicDNS"] = f"{protocol}://{magic}:{port}"
    
    logger.info(f"Generated shareable URLs: {urls}")
    return urls


def check_port_available(port: int, host: str = "0.0.0.0") -> bool:
    """
    Check if a port is available for binding.
    
    Args:
        port: Port number to check
        host: Host address to bind
        
    Returns:
        bool: True if port is available
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        sock.bind((host, port))
        sock.close()
        return True
    except OSError:
        return False


def get_tailscale_status() -> Dict[str, any]:
    """
    Get Tailscale connection status.
    
    Returns:
        Dict with status information
    """
    status = {
        "installed": False,
        "running": False,
        "ip": None,
        "hostname": None,
        "error": None
    }
    
    try:
        # Check if installed
        result = subprocess.run(
            ["tailscale", "status"],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        status["installed"] = True
        
        if result.returncode == 0:
            status["running"] = True
            status["ip"] = get_tailscale_ip()
            status["hostname"] = get_magicDNS_hostname()
        else:
            status["error"] = "Tailscale not connected"
            
    except FileNotFoundError:
        status["error"] = "Tailscale not installed"
    except subprocess.TimeoutExpired:
        status["installed"] = True
        status["error"] = "Tailscale check timed out"
    except Exception as e:
        status["error"] = str(e)
    
    return status
