# Prerequisites

Before starting the Network Fundamentals Lab course, ensure you have the following knowledge and tools.

## Required Knowledge

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

### On Your Linux System

| Tool | Purpose | Installation |
|------|---------|--------------|
| Docker | Container runtime | [docker.com](https://docker.com) |
| Containerlab | Network lab orchestration | [containerlab.dev](https://containerlab.dev) |
| Git | Version control | `apt install git` or [git-scm.com](https://git-scm.com) |
| Python 3 | Running tests | `apt install python3` |
| pytest | Test framework | `pip3 install pytest` |

### Network OS Images

The following images are pulled during setup:

- Nokia SR Linux (`ghcr.io/nokia/srlinux:24.10.1`)
- Additional images as needed per lesson

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

- [ ] Run `docker ps` and understand the output
- [ ] Run `containerlab version` successfully
- [ ] Clone a Git repository
- [ ] SSH into a remote machine (conceptual understanding)
- [ ] Explain what an IP address is (even if basics)

## What If I'm Missing Something?

### Missing Docker Knowledge

Review these concepts:
- [Docker Getting Started](https://docs.docker.com/get-started/)
- Lesson 0 of this course covers Docker networking specifically

### Missing Git Knowledge

Complete a Git basics tutorial:
- [Git Handbook](https://guides.github.com/introduction/git-handbook/)

### Missing Linux Knowledge

If you're new to Linux command line:
- [Linux Command Line Basics](https://ubuntu.com/tutorials/command-line-for-beginners)

## Ready to Start?

If you meet the prerequisites, proceed to:

1. [Linux Setup](linux-setup.md) - Install containerlab and Docker
2. [Fork Workflow](fork-workflow.md) - Set up your repository
3. [Lesson 0](../../lessons/clab/00-docker-networking/) - Begin learning!
