# Linux Setup for Network Labs

This guide explains how to set up your Linux environment for the Network Fundamentals Lab course.

## Overview

You will install containerlab and Docker directly on your Linux system. This provides a simple, native environment for running network labs.

## System Requirements

### Supported Operating Systems

- Ubuntu 20.04 LTS or newer
- Debian 11 or newer
- Fedora 35 or newer
- RHEL/CentOS 8 or newer

### Hardware Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| RAM | 8 GB | 16 GB |
| Disk Space | 20 GB free | 50 GB free |
| CPU Cores | 4 | 8 |

> **Note:** Network labs can be resource-intensive. Larger topologies in later lessons may require more resources.

## Installation Steps

### 1. Install Docker

Docker is required to run containerlab and network OS containers.

**Ubuntu/Debian:**

```bash
# Update package index
sudo apt-get update

# Install prerequisites
sudo apt-get install -y ca-certificates curl gnupg

# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add your user to docker group (avoids needing sudo)
sudo usermod -aG docker $USER
```

**Fedora:**

```bash
# Install Docker
sudo dnf -y install dnf-plugins-core
sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group
sudo usermod -aG docker $USER
```

> **Important:** Log out and back in after adding yourself to the docker group, or run `newgrp docker` to apply the group change immediately.

### 2. Verify Docker Installation

```bash
# Check Docker is running
docker version

# Test Docker works without sudo
docker run hello-world
```

Expected output should show Docker client and server versions, and the hello-world container should run successfully.

### 3. Install Containerlab

Install containerlab using the official installation script:

```bash
# Install containerlab
bash -c "$(curl -sL https://get.containerlab.dev)"

# Verify installation
containerlab version
```

Expected output:

```
                           _                   _       _     
                 _        (_)                 | |     | |    
 ____ ___  ____ | |_  ____ _ ____   ____  ____| | ____| | _  
/ ___) _ \|  _ \|  _)/ _  | |  _ \ / _  )/ ___) |/ _  | || \ 
( (__| |_|| | | | |_( ( | | | | | ( (/ /| |   | ( ( | | |_) )
\____)___/|_| |_|\___)_||_|_|_| |_|\____)_|   |_|\_||_|____/ 

    version: 0.60.1
     commit: ...
       date: ...
     source: https://github.com/srl-labs/containerlab
 rel. notes: https://containerlab.dev/rn/0.60/
```

### 4. Pull Network OS Images

Pull the SR Linux image used in this course:

```bash
# Pull Nokia SR Linux (free, no registration required)
docker pull ghcr.io/nokia/srlinux:24.10.1

# Verify the image is available
docker images | grep srlinux
```

> **Note:** The first pull may take several minutes depending on your internet connection. The SR Linux image is approximately 2 GB.

### 5. Install Additional Tools

Install tools needed for exercises and tests:

```bash
# Ubuntu/Debian
sudo apt-get install -y python3 python3-pip git

# Install pytest for running tests
pip3 install pytest
```

## Verification

Run these commands to verify your environment is ready:

```bash
# Docker is running
docker ps

# Containerlab is installed
containerlab version

# SR Linux image is available
docker images | grep srlinux

# Python and pytest are available
python3 --version
pytest --version

# Git is installed
git --version
```

All commands should complete without errors.

## Quick Test

Create a simple test topology to verify everything works:

```bash
# Create a test directory
mkdir -p ~/clab-test && cd ~/clab-test

# Create a minimal topology file
cat > test.clab.yml << 'EOF'
name: test
topology:
  nodes:
    srl:
      kind: nokia_srlinux
      image: ghcr.io/nokia/srlinux:24.10.1
EOF

# Deploy the lab
sudo containerlab deploy -t test.clab.yml

# Verify it's running
docker ps | grep clab

# Connect to the node
docker exec -it clab-test-srl sr_cli -c "show version"

# Clean up
sudo containerlab destroy -t test.clab.yml --cleanup
cd ~ && rm -rf ~/clab-test
```

If all commands complete successfully, your environment is ready for the course.

## Windows Users (WSL2)

If you're on Windows, you can run this course using Windows Subsystem for Linux 2 (WSL2).

### Install WSL2

```powershell
# Run in PowerShell as Administrator
wsl --install -d Ubuntu
```

Restart your computer when prompted.

### Configure WSL2

After restart, open Ubuntu from the Start menu and complete the initial setup (create username and password).

Then follow the Linux installation steps above inside WSL2.

### WSL2 Tips

- Access Windows files from WSL2 at `/mnt/c/Users/YourUsername/`
- Run VS Code in WSL2 with `code .` (requires VS Code WSL extension)
- Docker Desktop for Windows can integrate with WSL2, but native Docker in WSL2 works fine

## macOS Users

macOS users should use Docker Desktop for Mac with containerlab installed inside a Linux VM or container. For the best experience, consider using a Linux virtual machine with the steps above.

Alternatively, use a cloud-based Linux VM (AWS, GCP, Azure, DigitalOcean) for the course labs.

## Troubleshooting

### Permission Denied on Docker Commands

```bash
# Ensure you're in the docker group
groups | grep docker

# If not, add yourself and re-login
sudo usermod -aG docker $USER
# Log out and back in, or run:
newgrp docker
```

### Containerlab Deploy Fails

```bash
# Check Docker is running
sudo systemctl status docker

# If not running, start it
sudo systemctl start docker
```

### Image Pull Fails

```bash
# Check network connectivity
ping ghcr.io

# Check disk space
df -h

# Retry the pull
docker pull ghcr.io/nokia/srlinux:24.10.1
```

### Lab Cleanup Issues

```bash
# Force destroy all labs
sudo containerlab destroy --all --cleanup

# Remove orphaned containers
docker rm -f $(docker ps -aq --filter "name=clab")
```

## Next Steps

Once your environment is set up:

1. Complete [Fork Workflow](fork-workflow.md) to set up your repository
2. Start with [Lesson 0: Docker Networking](../../lessons/clab/00-docker-networking/)
