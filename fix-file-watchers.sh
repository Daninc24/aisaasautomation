#!/bin/bash

# Fix file watcher limits for development
echo "🔧 Fixing file watcher limits..."

# Check current limit
current_limit=$(cat /proc/sys/fs/inotify/max_user_watches)
echo "Current file watcher limit: $current_limit"

# Recommended limit
recommended_limit=524288

if [ "$current_limit" -lt "$recommended_limit" ]; then
    echo "Increasing file watcher limit to $recommended_limit..."
    
    # Temporary fix (until reboot)
    echo $recommended_limit | sudo tee /proc/sys/fs/inotify/max_user_watches
    
    # Permanent fix
    if ! grep -q "fs.inotify.max_user_watches" /etc/sysctl.conf; then
        echo "fs.inotify.max_user_watches=$recommended_limit" | sudo tee -a /etc/sysctl.conf
        echo "✅ Added permanent fix to /etc/sysctl.conf"
    else
        echo "✅ Permanent fix already exists in /etc/sysctl.conf"
    fi
    
    # Apply changes
    sudo sysctl -p
    
    echo "✅ File watcher limit increased to: $(cat /proc/sys/fs/inotify/max_user_watches)"
else
    echo "✅ File watcher limit is already sufficient: $current_limit"
fi

echo ""
echo "💡 Additional tips:"
echo "- Restart your development server after this fix"
echo "- Consider using Docker to avoid file watcher issues"
echo "- Exclude large directories like node_modules and venv from IDE indexing"