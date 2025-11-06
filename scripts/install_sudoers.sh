#!/bin/bash
# Install sudoers configuration for Homebrew Updater
# This script must be run manually with your password to configure passwordless sudo
# for specific brew operations.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SUDOERS_FILE="$PROJECT_DIR/config/homebrew-updater.sudoers"
TARGET="/etc/sudoers.d/homebrew-updater"

echo "=================================================="
echo "Homebrew Updater - Sudoers Installation"
echo "=================================================="
echo ""
echo "This script will configure passwordless sudo for:"
echo "  - brew cask upgrade operations"
echo "  - file removal operations used by brew"
echo "  - package installation/uninstallation"
echo ""
echo "Security note: This is limited to specific brew operations"
echo "and only applies to users in the 'admin' group."
echo ""
echo "This will require your password."
echo ""
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    exit 1
fi

# Validate syntax first
echo ""
echo "Validating sudoers syntax..."
if sudo visudo -cf "$SUDOERS_FILE"; then
    echo "✓ Syntax is valid"
else
    echo "✗ Syntax validation failed!"
    echo "Please check $SUDOERS_FILE for errors"
    exit 1
fi

# Install the file
echo ""
echo "Installing to $TARGET..."
sudo cp "$SUDOERS_FILE" "$TARGET"
sudo chmod 0440 "$TARGET"
sudo chown root:wheel "$TARGET"

echo ""
echo "✓ Sudoers configuration installed successfully!"
echo ""
echo "You can verify the installation with:"
echo "  sudo cat $TARGET"
echo ""
echo "To test passwordless sudo (should not prompt for password):"
echo "  sudo -n brew upgrade --cask --dry-run"
echo ""
