# Prerequisites

Before starting the Network Fundamentals Lab course, ensure you have the following knowledge and tools.

## Required Knowledge

### From DevPods Course

You should be comfortable with:

- Creating and managing DevPods/Dev Containers
- Understanding the devcontainer.json configuration
- Working with container-based development environments

### From Kubernetes Course

You should understand:

- Container fundamentals (images, containers, volumes)
- Basic kubectl commands
- Pod networking concepts (at a high level)

### Linux & Command Line

You should be able to:

- Navigate the filesystem (`cd`, `ls`, `pwd`)
- Edit files (`vim`, `nano`, or VS Code)
- Understand file permissions
- Use pipes and redirection
- Read man pages and --help output

### Git Basics

You should know how to:

- Clone repositories
- Create commits
- Push and pull changes
- Create branches (helpful but not required)

## Required Tools

### On Your Local Machine

| Tool | Purpose | Installation |
|------|---------|--------------|
| DevPod | Development environment | [devpod.sh](https://devpod.sh) |
| Git | Version control | `apt install git` or [git-scm.com](https://git-scm.com) |
| Docker | Container runtime | [docker.com](https://docker.com) or Podman |

### Provided in DevPod

The following are pre-installed in each lesson's DevPod:

- containerlab
- Docker CLI (Docker-in-Docker)
- Network OS images (pulled on first use)
- Python 3 with pytest
- Ansible
- Terraform (later lessons)

## Hardware Requirements

### Minimum

- 8 GB RAM
- 20 GB free disk space
- 4 CPU cores

### Recommended

- 16 GB RAM
- 50 GB free disk space
- 8 CPU cores

> **Note:** Network labs can be resource-intensive. Larger topologies in later lessons may require more resources.

## Network Requirements

- Internet access for pulling container images
- No specific ports need to be exposed
- Works behind most corporate firewalls

## Accounts (Free)

Some lessons use network operating systems that require free registration:

| Account | Required For | Registration |
|---------|--------------|--------------|
| GitHub | Fork workflow | [github.com](https://github.com) |
| Nokia (optional) | SR Linux docs | Auto-registers on doc access |

## Self-Assessment Checklist

Before starting, verify you can:

- [ ] Create a DevPod for a project
- [ ] Run `docker ps` and understand the output
- [ ] Clone a Git repository
- [ ] SSH into a remote machine (conceptual understanding)
- [ ] Explain what an IP address is (even if basics)

## What If I'm Missing Something?

### Missing DevPod Knowledge

Complete the DevPods fundamentals course first, or review:
- [DevPod Documentation](https://devpod.sh/docs)

### Missing Docker Knowledge

Review these concepts:
- [Docker Getting Started](https://docs.docker.com/get-started/)
- Lesson 0 of this course covers Docker networking specifically

### Missing Git Knowledge

Complete a Git basics tutorial:
- [Git Handbook](https://guides.github.com/introduction/git-handbook/)

## Ready to Start?

If you meet the prerequisites, proceed to:

1. [DevPod Setup](devpod-setup.md) - Configure your environment
2. [Fork Workflow](fork-workflow.md) - Set up your repository
3. [Lesson 0](../../lessons/clab/00-docker-networking/) - Begin learning!
