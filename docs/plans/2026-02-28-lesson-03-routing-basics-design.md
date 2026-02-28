# Lesson 03: Routing Basics -- Design Document

**Date:** 2026-02-28
**Status:** Approved

## Context

Lesson 02 ends with a deliberate cliffhanger: cross-subnet ping fails because routers only know their directly connected subnets. Lesson 03 resolves this by teaching static routing, routing tables, and multi-hop forwarding. The Ansible automation from lesson 02 is extended with a new routes template.

## Topology

Hub-and-spoke with 3 SR Linux routers and 3 Alpine hosts (6 nodes total).

```
  host1 -- srl1 (hub) -- srl2 -- host2
              |
             srl3 -- host3
```

srl1 is the hub with 3 interfaces. srl2 and srl3 are spokes, each with a host behind them. host1 connects directly to the hub.

### IP Addressing

| Subnet | Link | Left Device | Right Device |
|--------|------|-------------|--------------|
| `10.1.1.0/24` | host1 -- srl1 | host1: `eth1` = `10.1.1.2` | srl1: `e1-1` = `10.1.1.1` |
| `10.1.2.0/24` | srl1 -- srl2 | srl1: `e1-2` = `10.1.2.1` | srl2: `e1-1` = `10.1.2.2` |
| `10.1.3.0/24` | srl1 -- srl3 | srl1: `e1-3` = `10.1.3.1` | srl3: `e1-1` = `10.1.3.2` |
| `10.1.4.0/24` | srl2 -- host2 | srl2: `e1-2` = `10.1.4.1` | host2: `eth1` = `10.1.4.2` |
| `10.1.5.0/24` | srl3 -- host3 | srl3: `e1-2` = `10.1.5.1` | host3: `eth1` = `10.1.5.2` |

Convention: routers get `.1`, hosts get `.2`.

### Management IPs

| Node | Management IP |
|------|---------------|
| srl1 | 172.20.20.11 |
| srl2 | 172.20.20.12 |
| srl3 | 172.20.20.13 |

## Concepts Covered

1. **Routing table fundamentals** -- contents of a routing table, how routers decide where to send packets (longest prefix match), directly connected vs static routes
2. **Default gateways revisited** -- hosts had these in lesson 02; now explain why routers need routing entries too
3. **Static routes** -- SR Linux syntax, when to use them (small networks, stub networks)
4. **Multi-hop forwarding** -- trace host1 -> srl1 -> srl3 -> host3; each hop makes an independent routing decision
5. **Return path matters** -- reaching the destination is half the story; the reply must find its way back

## Ansible Extension

Extends the lesson 02 Ansible pattern (uri module + JSON-RPC + Jinja2).

### Changes from lesson 02

- **host_vars** get a `static_routes` section alongside `interfaces`
- **New template** `srl_routes.json.j2` generates static route CLI commands
- **Playbook** gets a second task applying routes after interfaces
- **Inventory** adds srl3

### Static Route Design

**srl1 (hub)** needs routes to host subnets behind spokes:
- `10.1.4.0/24` via `10.1.2.2` (host2 subnet via srl2)
- `10.1.5.0/24` via `10.1.3.2` (host3 subnet via srl3)

**srl2 (spoke)** needs routes for everything not directly connected:
- `10.1.1.0/24` via `10.1.2.1` (host1 subnet via hub)
- `10.1.3.0/24` via `10.1.2.1` (srl1-srl3 link via hub)
- `10.1.5.0/24` via `10.1.2.1` (host3 subnet via hub)

**srl3 (spoke)** mirrors srl2:
- `10.1.1.0/24` via `10.1.3.1` (host1 subnet via hub)
- `10.1.2.0/24` via `10.1.3.1` (srl1-srl2 link via hub)
- `10.1.4.0/24` via `10.1.3.1` (host2 subnet via hub)

**Hosts** have default routes via their local router (configured in topology exec, same as lesson 02).

## Exercises

### Exercise 1: Deploy, Configure, and Verify End-to-End

Deploy topology, run Ansible (interfaces + routes), verify host1 can ping host2 AND host3. This is the lesson 02 cliffhanger payoff.

### Exercise 2: Read the Routing Table

Examine `show network-instance default route-table` on each router. Trace the path from host2 to host3 through the hub. Explain each hop's routing decision.

### Exercise 3: Break/Fix -- Missing Route (Asymmetric)

Delete srl2's route to 10.1.5.0/24. host2 cannot reach host3, but host3 CAN reach host2 (via hub). Teaches: routing is per-hop, return path matters.

### Exercise 4: Break/Fix -- Wrong Next-Hop (Black Hole)

Change srl1's route to 10.1.5.0/24 to point at non-existent IP 10.1.3.99. Traffic to host3 is forwarded but never arrives. Teaches: router trusts its table; bad data = black hole.

### Exercise 5: Break/Fix -- Routing Loop

On srl2, point 10.1.5.0/24 at srl1. On srl1, point 10.1.5.0/24 at srl2. Packets bounce until TTL expires. Teaches: TTL prevents infinite loops, traceroute reveals loops.

### Exercise 6: Break/Fix -- Unreachable Next-Hop

Admin-disable the srl1-srl3 link. srl1 still has the route to 10.1.5.0/24 via 10.1.3.2, but the next-hop is unreachable because the interface is down. Teaches: route exists != path works.

## Tests

- `TestEnvironment` -- containerlab, docker, ansible, topology file
- `TestTopologyStructure` -- 6 nodes, 5 links, no latest tags, mgmt IPs, exec on hosts
- `TestAnsibleStructure` -- inventory, playbook, both templates, host_vars for 3 routers
- `TestLabDeployment` -- deploy, 6 containers running
- `TestConnectivity` -- host1->host2, host1->host3, host2->host3 (end-to-end through hub)

## Video Script Approach

Follow VIDEO_SCRIPT_TEMPLATE.md. Key sections:
1. Opening: "Last time, cross-subnet ping failed. Today we fix that."
2. Whiteboard: draw the hub-and-spoke, trace a packet hop by hop
3. Routing table demo: show directly connected routes, explain longest prefix match
4. Static route config: show SR Linux CLI, then show the Ansible/Jinja2 version
5. Live demo: deploy, configure, verify end-to-end ping
6. Recap + teaser for lesson 04 (BGP replaces static routes at scale)
