# Lesson 02: IP Fundamentals & Basic Connectivity -- Design

## Overview

Lesson 02 bridges conceptual networking knowledge (OSI model) with hands-on IP configuration using containerlab and Ansible. Students deploy a 4-node topology, apply IP configs via Ansible with Jinja2 templates, verify connectivity, and troubleshoot intentionally broken scenarios.

## Three Pillars

1. **OSI Layers 1-4** -- tied back to lesson 00 Linux primitives (veth = L1, bridge/MAC = L2, IP = L3, ports = L4)
2. **Ansible 101 with Jinja2** -- inventory, playbooks, templates, why automation beats manual config
3. **Hands-on IP configuration** -- deploy topology, apply configs, verify with ping/ARP, troubleshoot breakage

## Topology

```
host1 ---- srl1 ---- srl2 ---- host2
```

Three subnets:

| Subnet | Link | Left Device | Right Device |
|--------|------|-------------|--------------|
| `10.1.1.0/24` | host1 -- srl1 | host1: `eth1` = `10.1.1.2` | srl1: `e1-1` = `10.1.1.1` |
| `10.1.2.0/24` | srl1 -- srl2 | srl1: `e1-2` = `10.1.2.1` | srl2: `e1-1` = `10.1.2.2` |
| `10.1.3.0/24` | srl2 -- host2 | srl2: `e1-2` = `10.1.3.1` | host2: `eth1` = `10.1.3.2` |

Routers get `.1`, hosts get `.2`. Adjacent pings work. Cross-subnet ping (host1 to host2) intentionally does not work -- teaser for lesson 03 (routing).

## Video Script Structure (~14 min)

1. **Hook** (30s) -- "Your app says 'connection refused' -- is it a network problem or an app problem?"
2. **OSI Layers 1-4 Quick Tour** (3 min) -- map each layer to lesson 00 primitives
3. **IP Addressing & Subnets** (3 min) -- CIDR notation, subnet masks, "same network" test, ARP
4. **Ansible 101** (3 min) -- inventory, playbook YAML, Jinja2 templates, why template > hardcode
5. **Live Demo: Deploy & Configure** (3 min) -- deploy topology, run Ansible, verify with ping
6. **Verification Commands** (1 min) -- ping, ip addr, ARP table, SR Linux equivalents
7. **Recap + Teaser** (30s) -- adjacent pings work, but cross-subnet needs routing (lesson 03)

## Ansible Structure

```
02-ip-fundamentals/
  ansible/
    inventory.yml          # Groups: routers (srl1, srl2), hosts (host1, host2)
    playbook.yml           # Applies interface configs to all devices
    templates/
      srl_interfaces.j2   # SR Linux JSON CLI config from variables
      host_interfaces.j2  # Linux ip addr commands
    host_vars/
      srl1.yml            # Per-device interface/IP assignments
      srl2.yml
      host1.yml
      host2.yml
```

Students run the playbook (not write from scratch) but exercises ask them to modify the template.

## Exercises

1. **Deploy & Verify** -- deploy topology, run Ansible playbook, ping adjacent devices
2. **Read the Config** -- examine the Jinja2 template, predict output for srl2
3. **Add a Loopback** -- modify host_vars to add a loopback IP, re-run playbook, verify
4. **Break/Fix: Interface Down** -- interface is admin-disabled, diagnose and fix
5. **Break/Fix: Subnet Mismatch** -- mismatched /24 vs /30, diagnose why ping fails
6. **Break/Fix: Missing Gateway** -- host has IP but no default route, local works but cross-link fails

## Tests

- `TestEnvironment` -- containerlab, docker, ansible installed
- `TestTopologyStructure` -- YAML valid, 4 nodes, 3 links
- `TestAnsibleStructure` -- inventory, playbook, templates exist and are valid
- `TestLabDeployment` -- deploy succeeds, all containers running
- `TestConnectivity` -- adjacent ping works after config is applied

## Key Design Decisions

- **Routers = .1, hosts = .2** -- simple convention that's easy to remember
- **Three separate subnets** -- shows that each link is its own broadcast domain
- **Cross-subnet ping deliberately fails** -- creates a natural cliffhanger for lesson 03
- **Ansible runs configs, students read/modify** -- keeps focus on IP concepts while introducing automation
- **Jinja2 templates from day one** -- shows the value of templating before students have enough context to resist it
