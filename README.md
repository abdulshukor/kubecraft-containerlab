# Network Fundamentals Lab

A hands-on training series for DevOps engineers to learn networking fundamentals using containerlab and GitOps principles.

## About This Course

This course is designed for junior DevOps engineers who are comfortable with Docker, Linux, and Kubernetes but want to build stronger networking skills. Through hands-on labs using containerlab, you'll learn to:

- **Troubleshoot network issues** - Diagnose connectivity problems, read routing tables, trace paths
- **Design network topologies** - Create lab environments for testing network changes
- **Automate network configuration** - Apply GitOps principles to network infrastructure

## Prerequisites

Before starting this course, you should have completed:

- DevPods/Dev Containers fundamentals course
- Kubernetes basics course
- Familiarity with Docker and Linux command line

See [Prerequisites](docs/getting-started/prerequisites.md) for detailed requirements.

## Course Structure

| Lesson | Title | Topics |
|--------|-------|--------|
| 0 | [Docker Networking Fundamentals](lessons/clab/00-docker-networking/) | Network drivers, namespaces, Docker Compose |
| 1 | [Containerlab Primer](lessons/clab/01-containerlab-primer/) | Installation, topology files, first lab |
| 2 | IP Fundamentals & Connectivity | IP addressing, subnets, ping/traceroute |
| 3 | Routing Basics | Static routes, routing tables, Ansible |
| 4 | Data Center - Spine-Leaf | BGP, EVPN-VXLAN, Terraform |
| 5 | Cloud Provider Patterns | VPC simulation, hybrid connectivity |
| 6 | Edge & WAN Networking | Site-to-site, NAT, network services |
| 7 | Network Troubleshooting | Diagnostics, packet capture, pytest |
| 8 | Capstone Project | Full GitOps pipeline |

## Getting Started

1. **Fork this repository** - See [Fork Workflow](docs/getting-started/fork-workflow.md)
2. **Set up DevPod** - See [DevPod Setup](docs/getting-started/devpod-setup.md)
3. **Start with Lesson 0** - Navigate to `lessons/clab/00-docker-networking/`

## How to Use This Repo

Each lesson contains:

```
lessons/clab/XX-lesson-name/
├── README.md           # Lesson objectives and outline
├── .devcontainer/      # DevPod configuration
├── topology/           # Containerlab topology files
├── configs/            # Device configurations
├── exercises/          # Hands-on exercises
├── solutions/          # Exercise solutions
├── tests/              # Automated validation
└── transcript.md       # Video transcript
```

### Recommended Workflow

1. Watch the video lesson
2. Read the lesson README
3. Complete the exercises in `exercises/`
4. Run the tests to validate your work
5. Compare with solutions if stuck

## Quick Reference

- [Containerlab Cheatsheet](docs/reference/containerlab-cheatsheet.md)
- [SR Linux CLI Cheatsheet](docs/reference/srlinux-cheatsheet.md)
- [Network Commands Reference](docs/reference/network-commands.md)
- [Troubleshooting Guide](docs/reference/troubleshooting.md)

## External Resources

- [Containerlab Documentation](https://containerlab.dev)
- [Containerlab Discord](https://discord.gg/vAyddtaEV9)
- [Nokia SR Linux Documentation](https://documentation.nokia.com/srlinux/)
- [GitHub: containerlab topics](https://github.com/topics/containerlab)

## Contributing

This repo is designed for learning. If you find issues or have suggestions:

1. Open an issue describing the problem or suggestion
2. For exercise submissions, follow the [Contributing Guide](CONTRIBUTING.md)

## License

This training material is provided for educational purposes.
