#!/bin/bash

apt-get update -y

THIRD_PARTY_FOLDER=""

# Check if the folder exists
if [ ! -d "$THIRD_PARTY_FOLDER" ]; then
    echo "Third-party folder not found!"
    exit 1
fi

# Install all files in third party folder
for script_file in "$THIRD_PARTY_FOLDER"/*; do
    echo "Installing $script_file."
    if [[ $script_file == *.run ]]; then
        # If .run file, then change into executable and run
        chmod +x "$script_file"
        ./"$script_file" --mode unattended
    elif [[ $script_file == *.tar.gz ]]; then
        # Prompt the user for confirmation
        read -p "IMP MSG!!! Press any key and enter to continue" choice
        tar -xvzf $script_file
    elif [[ $script_file == *.py ]]; then
        continue
    else
        sudo apt-get install -y ./"$script_file"
    fi
done
echo "Installed third party files."

# Install additional XYZ packages if not present on system
if ! dpkg -s XYZ > /dev/null; then
    echo "Installing XYZ"
    sudo apt-get install -y XYZ
    sudo apt-get install -y XYZ
fi

echo "Installing XYZ."
export DEBIAN_FRONTEND=noninteractive
sudo apt-get -y install --no-install-recommends \
    pkg-config \
    libusb-1.0-0-dev

# Install Docker CLI
if ! docker --version; then
    # Add Docker's official GPG key:
    apt-get install ca-certificates curl
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    chmod a+r /etc/apt/keyrings/docker.asc

    # Add the repository to Apt sources:
    echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
    tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt-get update -y

    # TODO: install a specific version of Docker
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    sudo usermod -a -G docker $USER
fi

# Prompt the user for confirmation
read -p "Reboot of system recommended. Reboot now? (y/n): " choice
# Check the user's choice
if [ "$choice" = "y" ]; then
    echo "Rebooting..."
    sudo reboot
else
    echo "Auto-reboot cancelled. Please reboot computer prior to using test instruments."
fi
