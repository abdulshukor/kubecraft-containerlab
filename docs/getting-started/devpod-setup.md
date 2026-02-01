# DevPod Setup for Network Labs

This guide explains how to set up DevPod for the Network Fundamentals Lab course.

## Overview

Each lesson includes a `.devcontainer/` directory with a pre-configured environment. This ensures you have all the tools needed for that specific lesson.

## Quick Start

```bash
# Navigate to a lesson directory
cd lessons/clab/01-containerlab-primer

# Start the DevPod
devpod up .

# Connect to the DevPod
devpod ssh .
```

## DevPod Configuration

Each lesson's devcontainer includes:

```json
{
  "name": "Network Lab - Lesson X",
  "image": "ghcr.io/srl-labs/containerlab",
  "features": {
    "ghcr.io/devcontainers/features/docker-in-docker:2": {}
  },
  "postCreateCommand": "containerlab version",
  "remoteUser": "root"
}
```

### Key Components

| Component | Purpose |
|-----------|---------|
| `containerlab` base image | Pre-installed containerlab and dependencies |
| Docker-in-Docker | Run containers inside the DevPod |
| postCreateCommand | Verify installation on startup |

## First-Time Setup

### 1. Verify DevPod Installation

```bash
devpod version
```

If not installed, see [devpod.sh](https://devpod.sh) for installation instructions.

### 2. Configure Provider

DevPod needs a provider (where to run the containers):

```bash
# List available providers
devpod provider list

# Add Docker provider (most common)
devpod provider add docker
```

### 3. Test with Lesson 0

```bash
cd lessons/clab/00-docker-networking
devpod up .
```

## Working Inside the DevPod

### Connecting

```bash
# SSH into the DevPod
devpod ssh lesson-name

# Or use VS Code
devpod up . --ide vscode
```

### Verifying the Environment

Once connected, verify your tools:

```bash
# Check containerlab
containerlab version

# Check Docker
docker version

# Check network images (after first pull)
docker images | grep -E "srlinux|ceos|frr"
```

### Pulling Network Images

The first time you use a network OS image, it needs to be pulled:

```bash
# Nokia SR Linux (free, no auth required)
docker pull ghcr.io/nokia/srlinux:latest

# Note: Replace 'latest' with a specific version for production
# Check available tags at: https://github.com/nokia/srlinux-container-image
```

## Troubleshooting

### DevPod Won't Start

```bash
# Check Docker is running
docker ps

# Check for conflicting containers
docker ps -a | grep devpod

# Remove stale DevPod
devpod delete lesson-name
```

### Docker-in-Docker Issues

If containers won't start inside the DevPod:

```bash
# Verify Docker socket
ls -la /var/run/docker.sock

# Check Docker daemon
docker info
```

### Resource Issues

If the lab is slow or containers won't start:

```bash
# Check available resources
docker system df
docker system prune  # Clean up unused resources

# Increase Docker resources in Docker Desktop settings
```

### Network Image Pull Failures

```bash
# Check network connectivity
ping ghcr.io

# Retry with explicit registry
docker pull ghcr.io/nokia/srlinux:latest

# Check disk space
df -h
```

## DevPod Commands Reference

| Command | Purpose |
|---------|---------|
| `devpod up .` | Start DevPod for current directory |
| `devpod ssh .` | SSH into running DevPod |
| `devpod stop .` | Stop the DevPod |
| `devpod delete .` | Remove the DevPod |
| `devpod list` | Show all DevPods |
| `devpod logs .` | View DevPod logs |

## Multiple Lessons

You can have multiple DevPods running, but be mindful of resources:

```bash
# List all running DevPods
devpod list

# Stop lessons you're not actively using
devpod stop 00-docker-networking
```

## Customizing the Environment

If you need additional tools, you can modify the devcontainer:

```json
{
  "postCreateCommand": "apt-get update && apt-get install -y your-tool"
}
```

> **Note:** Changes to devcontainer.json require rebuilding:
> ```bash
> devpod delete . && devpod up .
> ```

## Next Steps

Once your DevPod is set up:

1. Complete [Fork Workflow](fork-workflow.md) to set up your repository
2. Start with [Lesson 0: Docker Networking](../../lessons/clab/00-docker-networking/)
