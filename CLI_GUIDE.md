# NinjaRMM CLI Tool - Quick Guide

A simple command-line interface for managing computers via NinjaRMM API.

## 🚀 Installation

Run the installer:
```bash
cd /home/user/1stproject
chmod +x install-cli.sh
./install-cli.sh
```

Choose where to install:
- **Option 1**: Desktop only
- **Option 2**: ~/.local/bin (accessible from anywhere)
- **Option 3**: Both (recommended)

## 📋 Commands

### Search for a Computer
```bash
ninja-cli search <name>
```
Examples:
```bash
ninja-cli search IT-GREGORYR
ninja-cli search "daniel 2019"
ninja-cli search greg
```

### Restart a Computer
```bash
ninja-cli restart <name>
```
Examples:
```bash
ninja-cli restart IT-GREGORYR
ninja-cli restart "OFFICE-PC"
```

### List All Computers
```bash
ninja-cli list
```

### List Computers with "guy" in Name
```bash
ninja-cli list-guy
```

### Get Detailed Computer Info
```bash
ninja-cli info <name>
```
Examples:
```bash
ninja-cli info IT-GREGORYR
ninja-cli info "daniel 2019"
```

### Show Help
```bash
ninja-cli --help
ninja-cli help
ninja-cli -h
```

## 🔐 Configuration

Before first use, update OAuth credentials in `ninja-cli.py`:

```python
CONFIG = {
    'client_id': 'YOUR_CLIENT_ID',
    'client_secret': 'YOUR_CLIENT_SECRET',
    ...
}
```

### How to Get Credentials:

1. Log in to NinjaRMM: https://comda.rmmservice.eu/auth/#/login
2. Go to: **Administration** → **Apps** → **API** → **Client App IDs**
3. Click **"Add"** to create new OAuth app
4. Set scopes: **Monitoring** and **Management**
5. Copy the Client ID and Client Secret
6. Update them in `ninja-cli.py` (lines 21-22)

## 📊 Output Format

### Search/List Output:
```
  [1] 🟢 IT-GREGORYR                              ID: 12345
  [2] 🔴 OFFICE-PC                                ID: 67890
```
- 🟢 = Online
- 🔴 = Offline

### Detailed Info Output:
```
==============================================================================
System Name:      IT-GREGORYR
DNS Name:         it-gregoryr.domain.com
Device ID:        12345
Node Class:       WINDOWS_WORKSTATION
Status:           🟢 Online
Last Contact:     2025-12-16T10:30:00Z

Organization:     My Company (ID: 1)
Operating System: Windows 10 Pro

Public IP:        203.0.113.42
IP Addresses:     192.168.1.100, 192.168.1.101

Manufacturer:     Dell Inc.
Model:            OptiPlex 7090
==============================================================================
```

## 🛠️ Troubleshooting

### "Client app not exist" Error
**Problem**: OAuth credentials are not configured in NinjaRMM.

**Solution**: Follow the Configuration steps above to create OAuth app.

### "Command not found"
**Problem**: CLI is not in your PATH.

**Solution**:
```bash
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

Or use the full path:
```bash
~/Desktop/ninja-cli search IT-GREGORYR
```

### "Authentication failed"
**Problem**: Invalid credentials.

**Solution**:
1. Check client_id and client_secret in `ninja-cli.py`
2. Verify the OAuth app exists in NinjaRMM admin panel
3. Ensure scopes include "monitoring" and "management"

### "Multiple computers found"
**Problem**: Search term matches multiple computers.

**Solution**: Be more specific with the computer name:
```bash
# Too broad
ninja-cli restart greg

# More specific
ninja-cli restart IT-GREGORYR
```

## 💡 Tips

1. **Partial Names**: Search works with partial names
   ```bash
   ninja-cli search greg    # Finds IT-GREGORYR
   ```

2. **Spaces in Names**: Use quotes for names with spaces
   ```bash
   ninja-cli search "daniel 2019"
   ```

3. **Quick Access**: Add alias to your shell config
   ```bash
   echo 'alias nc="ninja-cli"' >> ~/.bashrc
   source ~/.bashrc

   # Now you can use:
   nc search IT-GREGORYR
   nc restart IT-GREGORYR
   ```

4. **Case Insensitive**: Search is not case-sensitive
   ```bash
   ninja-cli search gregoryr    # Same as IT-GREGORYR
   ninja-cli search IT-gregoryr # Same as above
   ```

## 📁 Project Structure

```
/home/user/1stproject/
├── ninja-cli.py           # Main CLI tool
├── install-cli.sh         # Installation script
├── CLI_GUIDE.md           # This guide
├── restart-computer.py    # Standalone restart script
├── search-computer.py     # Standalone search script
└── get-guy-machines.py    # List machines with "guy"
```

## 🔗 Related Files

- **ninja-api.py** - Base API integration
- **NINJA_API_README.md** - Full API documentation
- **restart-computer.py** - Standalone restart script
- **search-computer.py** - Standalone search script

## 📞 Support

For NinjaRMM API questions:
- Email: [email protected]
- Documentation: https://app.ninjarmm.com/apidocs/

## 🎯 Quick Reference Card

| Command | Description |
|---------|-------------|
| `ninja-cli search <name>` | Find computers by name |
| `ninja-cli restart <name>` | Reboot a computer |
| `ninja-cli list` | Show all computers |
| `ninja-cli list-guy` | Show computers with "guy" |
| `ninja-cli info <name>` | Detailed computer info |
| `ninja-cli --help` | Show help |

---

**Version**: 1.0
**Last Updated**: 2025-12-16
