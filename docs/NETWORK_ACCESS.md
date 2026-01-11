# Network Access Guide

## Overview

DexTalker can be accessed from other devices on your local network (LAN) or Tailscale network (Tailnet).

---

## Quick Start

### 1. Enable Network Access

1. Navigate to **⚙️ Network Access** tab
2. Check **Enable LAN Access** or **Enable Tailnet Access**
3. Click **💾 Save Settings**
4. **Restart** DexTalker for changes to take effect

### 2. Share the URL

1. Copy the appropriate URL from the **Shareable Addresses** panel:
   - **LAN**: Use with devices on same Wi-Fi
   - **Tailnet**: Use with devices on your Tailscale network
2. Share the URL and access token with the remote user

### 3. Remote Access

1. Open the shared URL in a browser
2. Enter the access token when prompted
3. Use DexTalker normally

---

## LAN Access

### Prerequisites
- DexTalker and remote device on same Wi-Fi/Ethernet
- Firewall allows inbound connections on port (default: 7860)

### Setup
1. Enable **LAN Access** in settings
2. Note your LAN URL (e.g., `http://192.168.1.42:7860`)
3. Share URL and access token
4. Remote user opens URL and logs in

### Troubleshooting

**URL not reachable**:
- Check firewall settings (allow port 7860)
- Verify devices on same network
- Try localhost on host machine first

**"Network access disabled" error**:
- Ensure LAN Access is enabled
- Click "Save Settings" and restart

---

## Tailnet Access (Recommended)

### Prerequisites
- Tailscale installed on both devices
- Both devices logged into same Tailnet

### Setup
1. Install Tailscale: https://tailscale.com/download
2. Enable **Tailnet Access** in settings
3. Optionally enable **Tailnet-Only Mode** for extra security
4. Note your Tailscale URL:
   - IP format: `http://100.64.x.x:7860`
   - MagicDNS: `http://hostname.tail-abc.ts.net:7860`
5. Share URL and access token
6. Remote user opens URL and logs in

### Why Tailnet is Recommended
- ✅ Works from anywhere (not just local network)
- ✅ Encrypted by default
- ✅ No port forwarding required
- ✅ No firewall configuration needed
- ✅ MagicDNS provides easy-to-remember hostnames

### Troubleshooting

**"No Tailscale IP detected"**:
```bash
# Check Tailscale status
tailscale status

# If offline, reconnect
tailscale up
```

**MagicDNS not available**:
- Enable MagicDNS in Tailscale admin: https://login.tailscale.com/admin/dns
- Restart DexTalker

---

## Security

### Access Token
- **Required** for all remote connections
- Generated automatically on first launch
- Regenerate anytime in Network Access settings
- Keep confidential - treat like a password

### Tailnet-Only Mode
- **Recommended** for maximum security
- Rejects all non-Tailscale connections
- Ensures only your Tailnet devices can connect

### Best Practices
1. Only share token with trusted users
2. Regenerate token if compromised
3. Use Tailnet instead of LAN when possible
4. Keep "Require Login" enabled
5. Disable network access when not needed

---

## Firewall Configuration

### macOS
```bash
# Allow inbound on port 7860
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /path/to/dextalker
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /path/to/dextalker
```

### Linux (ufw)
```bash
sudo ufw allow 7860/tcp
```

### Windows
1. Windows Defender Firewall → Advanced Settings
2. Inbound Rules → New Rule
3. Port → TCP → 7860
4. Allow the connection

---

## Advanced

### Custom Port
1. Change port in Network Access settings
2. Update firewall rules
3. Restart DexTalker
4. Use new URLs with custom port

### Bind Address
- `127.0.0.1`: Localhost only (default when disabled)
- `0.0.0.0`: All interfaces (when LAN/Tailnet enabled)

### Multiple Users
- All remote users share same access token
- Individual user accounts not yet supported
- Token gives full access to DexTalker features

---

## FAQ

**Q: Can I use both LAN and Tailnet?**  
A: Yes, enable both. Tailnet-Only mode disables LAN.

**Q: Does this work over the internet?**  
A: Only via Tailnet. LAN is local network only.

**Q: Is it secure?**  
A: Yes, with token authentication. Tailnet adds encryption.

**Q: Can I use HTTPS?**  
A: Not yet. Add SSL termination via reverse proxy (nginx, Caddy).

**Q: Does it work on mobile?**  
A: Yes, any browser. Tailscale apps available for iOS/Android.

---

## Support

- Issues: https://github.com/westkitty/DexTalker/issues
- Check logs: `dextalker.log`
- Test localhost first before debugging network issues
