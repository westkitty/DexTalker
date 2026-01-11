"""
Authentication system for DexTalker network access.
Provides token-based auth and access control for LAN/Tailnet connections.
"""
import secrets
import logging
from typing import Optional, Dict
from datetime import datetime, timedelta
from pathlib import Path
import json

logger = logging.getLogger("DexTalker.Auth")


def generate_access_token() -> str:
    """
    Generate a cryptographically secure access token.
    
    Returns:
        str: URL-safe 32-byte token
    """
    return secrets.token_urlsafe(32)


def verify_access_token(provided: str, expected: str) -> bool:
    """
    Verify an access token using constant-time comparison.
    
    Args:
        provided: Token provided by user
        expected: Expected/stored token
        
    Returns:
        bool: True if tokens match
    """
    return secrets.compare_digest(provided, expected)


class NetworkAuth:
    """
    Manages authentication and access control for network connections.
    """
    
    def __init__(self, data_dir: Path):
        """
        Initialize network auth manager.
        
        Args:
            data_dir: Directory for storing auth data
        """
        self.data_dir = Path(data_dir)
        self.auth_file = self.data_dir / "network_auth.json"
        self.access_token = None
        self.config = {
            "lan_enabled": False,
            "tailnet_enabled": False,
            "tailnet_only": False,
            "require_login": True,
            "port": 7860,
            "bind_address": "127.0.0.1"
        }
        
        self._load_config()
    
    def _load_config(self):
        """Load auth configuration from file."""
        if self.auth_file.exists():
            try:
                with open(self.auth_file, 'r') as f:
                    data = json.load(f)
                    self.access_token = data.get("access_token")
                    self.config.update(data.get("config", {}))
                    logger.info("Loaded network auth configuration")
            except Exception as e:
                logger.error(f"Failed to load auth config: {e}")
        
        # Generate token if missing
        if not self.access_token:
            self.access_token = generate_access_token()
            self._save_config()
    
    def _save_config(self):
        """Save auth configuration to file."""
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            data = {
                "access_token": self.access_token,
                "config": self.config,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.auth_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.info("Saved network auth configuration")
        except Exception as e:
            logger.error(f"Failed to save auth config: {e}")
    
    def regenerate_token(self) -> str:
        """
        Generate a new access token.
        
        Returns:
            str: New access token
        """
        self.access_token = generate_access_token()
        self._save_config()
        logger.info("Regenerated access token")
        return self.access_token
    
    def update_config(self, **kwargs):
        """
        Update network configuration.
        
        Args:
            **kwargs: Configuration keys to update
        """
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
        
        # Update bind address based on enabled modes
        if self.config["lan_enabled"] or self.config["tailnet_enabled"]:
            self.config["bind_address"] = "0.0.0.0"
        else:
            self.config["bind_address"] = "127.0.0.1"
        
        self._save_config()
        logger.info(f"Updated network config: {kwargs}")
    
    def check_access(self, client_ip: str, provided_token: Optional[str] = None) -> tuple[bool, str]:
        """
        Check if a client IP should be granted access.
        
        Args:
            client_ip: Client's IP address
            provided_token: Access token provided by client
            
        Returns:
            Tuple of (allowed: bool, reason: str)
        """
        from .utils import is_localhost, is_tailscale_ip, is_lan_ip
        
        # Localhost always allowed
        if is_localhost(client_ip):
            return True, "localhost"
        
        # Check if network access is enabled
        if not self.config["lan_enabled"] and not self.config["tailnet_enabled"]:
            return False, "Network access disabled"
        
        # Check token if required
        if self.config["require_login"]:
            if not provided_token:
                return False, "Authentication required"
            
            if not verify_access_token(provided_token, self.access_token):
                return False, "Invalid token"
        
        # Check Tailnet-only mode
        if self.config["tailnet_only"]:
            if not is_tailscale_ip(client_ip):
                return False, "Tailnet-only mode enabled"
            return True, "tailnet"
        
        # Check Tailnet access
        if is_tailscale_ip(client_ip):
            if self.config["tailnet_enabled"]:
                return True, "tailnet"
            return False, "Tailnet access disabled"
        
        # Check LAN access
        if is_lan_ip(client_ip):
            if self.config["lan_enabled"]:
                return True, "lan"
            return False, "LAN access disabled"
        
        # Reject all other IPs
        return False, "IP not in allowed ranges"
    
    def get_config(self) -> Dict:
        """Get current configuration."""
        return self.config.copy()
    
    def get_token(self) -> str:
        """Get current access token."""
        return self.access_token
