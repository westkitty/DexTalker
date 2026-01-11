"""
Unit tests for network utilities and authentication.
"""
import pytest
from app.network.utils import (
    is_tailscale_ip,
    is_localhost,
    is_lan_ip,
    generate_shareable_urls,
    check_port_available
)
from app.network.auth import (
    generate_access_token,
    verify_access_token,
    NetworkAuth
)
from pathlib import Path
import tempfile


class TestNetworkUtils:
    """Test network utility functions."""
    
    def test_is_tailscale_ip(self):
        """Test Tailscale IP detection."""
        assert is_tailscale_ip("100.64.0.1") == True
        assert is_tailscale_ip("100.127.255.255") == True
        assert is_tail scale_ip("192.168.1.1") == False
        assert is_tailscale_ip("127.0.0.1") == False
        assert is_tailscale_ip("invalid") == False
    
    def test_is_localhost(self):
        """Test localhost detection."""
        assert is_localhost("127.0.0.1") == True
        assert is_localhost("::1") == True
        assert is_localhost("localhost") == True
        assert is_localhost("192.168.1.1") == False
    
    def test_is_lan_ip(self):
        """Test LAN IP detection."""
        assert is_lan_ip("192.168.1.1") == True
        assert is_lan_ip("10.0.0.1") == True
        assert is_lan_ip("172.16.0.1") == True
        assert is_lan_ip("8.8.8.8") == False
        assert is_lan_ip("127.0.0.1") == False
    
    def test_generate_shareable_urls(self):
        """Test URL generation."""
        urls = generate_shareable_urls(7860)
        
        assert "localhost" in urls
        assert urls["localhost"] == "http://127.0.0.1:7860"
        assert urls["localhost"].startswith("http://")
        assert ":7860" in urls["localhost"]
    
    def test_check_port_available(self):
        """Test port availability check."""
        # Port 1 is usually unavailable (requires root)
        # This test is platform-dependent
        result = check_port_available(1)
        assert isinstance(result, bool)


class TestNetworkAuth:
    """Test authentication system."""
    
    def test_generate_token(self):
        """Test token generation."""
        token = generate_access_token()
        assert len(token) >= 32
        assert isinstance(token, str)
        
        # Tokens should be unique
        token2 = generate_access_token()
        assert token != token2
    
    def test_verify_token(self):
        """Test token verification."""
        token = "test_token_12345"
        
        assert verify_access_token(token, token) == True
        assert verify_access_token(token, "wrong_token") == False
        assert verify_access_token("", token) == False
    
    def test_network_auth_init(self):
        """Test NetworkAuth initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            auth = NetworkAuth(Path(tmpdir))
            
            assert auth.access_token is not None
            assert len(auth.access_token) >= 32
            assert auth.config["lan_enabled"] == False
            assert auth.config["tailnet_enabled"] == False
    
    def test_network_auth_config_update(self):
        """Test configuration updates."""
        with tempfile.TemporaryDirectory() as tmpdir:
            auth = NetworkAuth(Path(tmpdir))
            
            auth.update_config(lan_enabled=True, port=8080)
            
            assert auth.config["lan_enabled"] == True
            assert auth.config["port"] == 8080
            assert auth.config["bind_address"] == "0.0.0.0"
    
    def test_check_access_localhost(self):
        """Test localhost access always allowed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            auth = NetworkAuth(Path(tmpdir))
            
            allowed, reason = auth.check_access("127.0.0.1")
            assert allowed == True
            assert reason == "localhost"
    
    def test_check_access_lan_disabled(self):
        """Test LAN access when disabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            auth = NetworkAuth(Path(tmpdir))
            
            allowed, reason = auth.check_access("192.168.1.100")
            assert allowed == False
            assert "disabled" in reason.lower()
    
    def test_check_access_lan_with_token(self):
        """Test LAN access with valid token."""
        with tempfile.TemporaryDirectory() as tmpdir:
            auth = NetworkAuth(Path(tmpdir))
            auth.update_config(lan_enabled=True)
            
            allowed, reason = auth.check_access("192.168.1.100", auth.access_token)
            assert allowed == True
            assert reason == "lan"
    
    def test_check_access_invalid_token(self):
        """Test access with invalid token."""
        with tempfile.TemporaryDirectory() as tmpdir:
            auth = NetworkAuth(Path(tmpdir))
            auth.update_config(lan_enabled=True)
            
            allowed, reason = auth.check_access("192.168.1.100", "wrong_token")
            assert allowed == False
            assert "invalid" in reason.lower() or "token" in reason.lower()
    
    def test_tailnet_only_mode(self):
        """Test Tailnet-only mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            auth = NetworkAuth(Path(tmpdir))
            auth.update_config(tailnet_only=True, tailnet_enabled=True)
            
            # Tailscale IP with token should work
            allowed, _ = auth.check_access("100.64.0.1", auth.access_token)
            assert allowed == True
            
            # Non-Tailscale IP should be rejected
            allowed, reason = auth.check_access("192.168.1.100", auth.access_token)
            assert allowed == False
