#!/bin/bash

# NinjaRMM CLI Installer
# This script installs the ninja-cli tool to your desktop and PATH

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║           NinjaRMM CLI Installer                               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLI_SCRIPT="$SCRIPT_DIR/ninja-cli.py"

# Check if the CLI script exists
if [ ! -f "$CLI_SCRIPT" ]; then
    echo "❌ Error: ninja-cli.py not found in $SCRIPT_DIR"
    exit 1
fi

# Make the CLI script executable
echo "🔧 Making ninja-cli.py executable..."
chmod +x "$CLI_SCRIPT"

# Create a symlink in user's local bin (or Desktop)
INSTALL_DIR="$HOME/Desktop"
SYMLINK_PATH="$INSTALL_DIR/ninja-cli"

# Also try to install to ~/.local/bin if it exists
LOCAL_BIN="$HOME/.local/bin"

echo ""
echo "📦 Installation Options:"
echo "  1. Install to Desktop ($INSTALL_DIR)"
echo "  2. Install to ~/.local/bin (accessible from anywhere)"
echo "  3. Both"
echo ""
read -p "Choose option (1/2/3) [3]: " choice
choice=${choice:-3}

# Install to Desktop
if [ "$choice" = "1" ] || [ "$choice" = "3" ]; then
    echo ""
    echo "🖥️  Installing to Desktop..."

    # Create Desktop directory if it doesn't exist
    mkdir -p "$INSTALL_DIR"

    # Create symlink
    ln -sf "$CLI_SCRIPT" "$SYMLINK_PATH"

    if [ -f "$SYMLINK_PATH" ]; then
        echo "✅ Installed to: $SYMLINK_PATH"
        echo "   You can run: ~/Desktop/ninja-cli <command>"
    else
        echo "❌ Failed to install to Desktop"
    fi
fi

# Install to ~/.local/bin
if [ "$choice" = "2" ] || [ "$choice" = "3" ]; then
    echo ""
    echo "📂 Installing to ~/.local/bin..."

    # Create ~/.local/bin if it doesn't exist
    mkdir -p "$LOCAL_BIN"

    # Create symlink
    ln -sf "$CLI_SCRIPT" "$LOCAL_BIN/ninja-cli"

    if [ -f "$LOCAL_BIN/ninja-cli" ]; then
        echo "✅ Installed to: $LOCAL_BIN/ninja-cli"

        # Check if ~/.local/bin is in PATH
        if [[ ":$PATH:" == *":$LOCAL_BIN:"* ]]; then
            echo "   You can run: ninja-cli <command>"
        else
            echo "   ⚠️  Note: $LOCAL_BIN is not in your PATH"
            echo "   Add this to your ~/.bashrc or ~/.zshrc:"
            echo "   export PATH=\"\$HOME/.local/bin:\$PATH\""
            echo ""
            echo "   Or run: echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc"
            echo "   Then: source ~/.bashrc"
        fi
    else
        echo "❌ Failed to install to ~/.local/bin"
    fi
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                  Installation Complete!                        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📚 Usage Examples:"
echo "   ninja-cli search IT-GREGORYR"
echo "   ninja-cli restart IT-GREGORYR"
echo "   ninja-cli list-guy"
echo "   ninja-cli info \"daniel 2019\""
echo "   ninja-cli list"
echo "   ninja-cli --help"
echo ""
echo "🔐 Note: Make sure to update OAuth credentials in ninja-cli.py"
echo "   Edit: $CLI_SCRIPT"
echo "   Lines 21-22 (client_id and client_secret)"
echo ""
