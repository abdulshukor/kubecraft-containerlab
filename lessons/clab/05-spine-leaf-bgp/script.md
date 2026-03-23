# Lesson 5: Spine-Leaf Networking with BGP - Video Script

## Lesson Information

| Field | Value |
|-------|-------|
| **Lesson Number** | 05 |
| **Title** | Spine-Leaf Networking with BGP |
| **Duration Target** | 13-15 minutes |
| **Prerequisites** | Lessons 0-4, gNMIc installed (`gnmic version`), 16 GB RAM |
| **Learning Objectives** | Explain Clos architecture, configure eBGP underlay on a 6-router fabric, observe ECMP across spines, diagnose fabric resilience under spine failure |

---

## Pre-Recording Checklist

- [ ] Lab environment tested (containerlab installed, Docker running)
- [ ] gNMIc installed: `gnmic version`
- [ ] Lesson 04 lab destroyed: `containerlab destroy --all`
- [ ] SR Linux image pulled: `docker pull ghcr.io/nokia/srlinux:24.10.1`
- [ ] Alpine image pulled: `docker pull alpine:3.20`
- [ ] Minimum 16 GB RAM available: `free -h`
- [ ] Screen resolution set (1920x1080)
- [ ] Terminal font size increased (14-16pt)
- [ ] Notifications disabled
- [ ] Clean terminal: `clear && history -c`
- [ ] No labs running: `containerlab inspect --all`

---

## Script

### Opening Hook (30 seconds)

> **[VOICEOVER - Terminal visible]**
>
> "Last lesson, you configured BGP on 3 routers and watched them exchange routes. That was the mechanics. Today we use those mechanics to build something real -- a spine-leaf fabric. In a data center, every server needs to reach every other server with predictable latency and maximum bandwidth. Spine-leaf delivers both: equal-cost paths between every pair of racks, all links active, no wasted capacity. This is the topology running under every major cloud provider and every large-scale Kubernetes deployment."

**Visual:** Terminal showing lesson 04 triangle topology diagram, then transition to spine-leaf diagram

---

### Section 1: Why Spine-Leaf? (2 minutes)

> **[VOICEOVER]**
>
> "By the end of lesson 4, our 3 routers were fully meshed -- every router directly connected to every other. That gives you redundancy, but it only works at small scale. Real data centers with hundreds of racks never tried to full-mesh their switches.
>
> Instead, they used a 3-tier architecture: core, distribution, and access layers. But those designs relied on Spanning Tree Protocol, which blocks redundant links to prevent loops. You pay for redundant cables, then STP disables half of them. Wasteful.
>
> Clos spine-leaf architecture -- named after Charles Clos, who published this non-blocking switch design in 1953 -- solves this. You split the network into two tiers: spines and leaves. Every leaf connects to every spine, but there are no leaf-to-leaf or spine-to-spine links. Every path between any two leaves crosses exactly one spine. And because all paths are equal length, the router can use ECMP -- equal-cost multipath -- to load-balance across all spines simultaneously. No blocked links. No wasted bandwidth.
>
> The key insight: to add more bandwidth, add more spines. To add more servers, add more leaves. Each tier scales independently."

**Visual:** Two diagrams side by side -- 3-tier with STP (blocked links in red), Clos (all links green/active)

**Key Points:**
- 3-tier + STP: blocks redundant links, wastes capacity
- Clos (Charles Clos, 1953): structured 2-tier, all links active via ECMP, tiers scale independently
- Horizontal scaling: spines add bandwidth, leaves add server ports

**Transition:** "But what routing protocol runs this fabric? Let's look at the design choices."

---

### Section 2: BGP Design Choices (90 seconds)

> **[VOICEOVER]**
>
> "We need a routing protocol for this fabric. Lesson 4 used eBGP -- external BGP. Could we use iBGP -- internal BGP -- instead? If every device shared one AS number, all sessions would be iBGP. But iBGP has a catch: a router will not re-advertise a route learned from one iBGP peer to another. If leaf1 tells spine1 about its host subnet, spine1 would not pass it to leaf2. To fix this, you'd need either a full mesh of iBGP sessions between all devices, or a route reflector -- a designated router that's allowed to break that rule. Both add complexity.
>
> RFCs -- Requests for Comments -- are how the internet's protocols are documented and standardized. They are the primary source of truth for how things actually work. If you take one habit from this course, make it reading RFCs.
>
> RFC 7938, published in 2016, documents how large-scale data centers like Microsoft and Facebook solved this: use eBGP for everything. eBGP requires different AS numbers on each side of a session -- that's what makes it external. So each leaf gets its own ASN. The spines share a single ASN -- they never peer with each other, so there's no iBGP between them. Every spine-leaf link crosses an AS boundary, making it eBGP.
>
> The result: routes are re-advertised freely, no route reflectors needed. Loop prevention comes free through AS-path. And because all spines share one ASN, the AS-path through any spine looks identical -- which is exactly what ECMP needs to treat them as equal-cost paths."

**Visual:** Diagram showing iBGP limitation (spine won't re-advertise) vs eBGP (spine freely re-advertises)

**Key Points:**
- iBGP won't re-advertise between peers without route reflectors
- RFC 7938: eBGP-only underlay, unique ASN per leaf, shared ASN for all spines
- Shared spine ASN gives identical AS-paths = natural ECMP

**Transition:** "Let's look at the specific design of our fabric."

---

### Section 3: Our Fabric (90 seconds)

> **[VOICEOVER]**
>
> "Here's our fabric: 2 spines, 4 leaves, 4 hosts. Every leaf connects to every spine -- that's 8 links. Each link gets a /31 point-to-point subnet, just like lesson 4. Each leaf also connects to one host on a /24 subnet.
>
> Both spines share AS 65000. Leaves are AS 65001 through 65004 -- each leaf its own autonomous system, as RFC 7938 recommends. Every spine-leaf link is an eBGP session. A peer-group is a template that applies the same BGP settings to multiple neighbors. The spines' peer-group is called 'leaves' with 4 neighbors each. The leaves' peer-group is called 'spines' with 2 neighbors each. Total: 8 BGP sessions across the fabric.
>
> Each router also gets a router-ID -- a unique 32-bit identifier, set to a loopback-style IP, that BGP uses to identify the router in the network."

**Visual:** Topology diagram with AS numbers labeled, /31 subnets on links, /24 subnets on host segments

```
     spine1 (AS 65000)    spine2 (AS 65000)
       / |    \    \       / |    \    \
    leaf1  leaf2  leaf3  leaf4
  (65001) (65002) (65003) (65004)
     |       |       |       |
   host1   host2   host3   host4
```

**Key Points:**
- /31 point-to-point links between every spine-leaf pair
- RFC 7938: shared spine ASN (65000), unique leaf ASNs (65001-65004), every link is eBGP
- 8 total BGP sessions (4 leaves x 2 spines)
- Shared spine ASN gives identical AS-paths, enabling ECMP

**Transition:** "Let's deploy this and see it work."

---

### Section 4: Deploying the Fabric (2 minutes)

> **[VOICEOVER]**
>
> "The topology file defines 10 containers: 6 SR Linux routers and 4 Alpine hosts. Startup configs in the topology/configs directory handle the base interface addressing -- each router's /31 uplinks and /24 host-facing interface are pre-configured. BGP is not configured yet. We'll apply that separately with gNMIc, just like lesson 4."

```bash
cd lessons/clab/05-spine-leaf-bgp
containerlab deploy -t topology/lab.clab.yml
```

**Expected output:** Table showing 10 running containers

> "10 containers are up. Let's verify that cross-leaf connectivity doesn't work yet -- without BGP, the leaves don't know about each other's host subnets."

```bash
docker exec clab-spine-leaf-bgp-host1 ping -c 2 -W 3 10.20.4.2
```

> "Ping fails. leaf1 has no route to 10.20.4.0/24. The fabric is physically wired, but without BGP, no routes are exchanged. Same lesson we learned in lesson 2 -- wires alone don't create connectivity."

**Visual:** Terminal showing deploy output and failed ping

**Transition:** "Now let's light up BGP across the entire fabric."

---

### Section 5: Live Demo -- Configure and Verify (3 minutes)

> **[VOICEOVER]**
>
> "Six gNMIc commands, one per router. Each config file creates three routing policies and chains them together -- same pattern we used in lesson 4, but worth a closer look now that 6 routers depend on it.
>
> The export policies are chained as a list: export-connected runs first. If a route is a connected host /24 matching the host-subnets prefix-set, accept it. If not, the next-policy default action passes it to export-bgp, which accepts BGP-learned routes. This chain is what makes spines work as transit routers -- without export-bgp, a spine would learn leaf1's host subnet but never announce it to the other leaves. SR Linux has a default-deny export policy, so nothing gets advertised unless you explicitly allow it.
>
> The host-subnets prefix-set filters out /31 fabric link prefixes from export-connected -- those are already known via direct connection on each router and don't need to be in BGP. Only the /24 host subnets get advertised.
>
> Each config also enables the IPv4 unicast address family with multipath for ECMP, and configures BGP with the correct AS, router-ID, peer-group, and neighbors."

```bash
cd gnmic
gnmic -a clab-spine-leaf-bgp-spine1:57400 set --request-file configs/spine1-bgp.json
gnmic -a clab-spine-leaf-bgp-spine2:57400 set --request-file configs/spine2-bgp.json
gnmic -a clab-spine-leaf-bgp-leaf1:57400 set --request-file configs/leaf1-bgp.json
gnmic -a clab-spine-leaf-bgp-leaf2:57400 set --request-file configs/leaf2-bgp.json
gnmic -a clab-spine-leaf-bgp-leaf3:57400 set --request-file configs/leaf3-bgp.json
gnmic -a clab-spine-leaf-bgp-leaf4:57400 set --request-file configs/leaf4-bgp.json
```

> "All six applied. Let's check the sessions. I'll start with spine1 -- it should have 4 established sessions, one to each leaf."

```bash
docker exec -it clab-spine-leaf-bgp-spine1 sr_cli -c \
  "show network-instance default protocols bgp neighbor"
```

> "Four neighbors, all Established. Now leaf1 -- it should have 2 sessions, one to each spine."

```bash
docker exec -it clab-spine-leaf-bgp-leaf1 sr_cli -c \
  "show network-instance default protocols bgp neighbor"
```

> "Two sessions, both Established. Now let's look at the routing table on leaf1."

```bash
docker exec -it clab-spine-leaf-bgp-leaf1 sr_cli -c \
  "show network-instance default route-table ipv4-unicast summary"
```

> "This is the key moment. Look at the remote host subnets -- 10.20.2.0/24, 10.20.3.0/24, 10.20.4.0/24. Each one shows two next-hops: one via spine1 at 10.10.1.0, one via spine2 at 10.10.2.0. That's ECMP. The router will hash traffic flows across both spines for load distribution.
>
> Now the connectivity test."

```bash
docker exec clab-spine-leaf-bgp-host1 ping -c 3 10.20.2.2
docker exec clab-spine-leaf-bgp-host1 ping -c 3 10.20.3.2
docker exec clab-spine-leaf-bgp-host1 ping -c 3 10.20.4.2
```

> "All three succeed. host1 can reach host2, host3, and host4 -- all on different leaves, all going through the spine tier. Notice TTL is 61: starting at 64, decremented once by each of the 3 routers in the path -- leaf1, the spine, and leaf4. The leaf-to-leaf path is 2 fabric hops, but hosts see 3 router hops end-to-end."

**Visual:** Full terminal showing BGP neighbors, routing table with ECMP entries, successful pings

---

### Section 6: Live Demo -- Spine Failure (2 minutes)

> **[VOICEOVER]**
>
> "The whole point of a multi-spine fabric is resilience. Let's take down spine1 and watch what happens."

```bash
docker exec -it clab-spine-leaf-bgp-spine1 sr_cli
```

```
enter candidate
set / interface ethernet-1/1 admin-state disable
set / interface ethernet-1/2 admin-state disable
set / interface ethernet-1/3 admin-state disable
set / interface ethernet-1/4 admin-state disable
commit now
exit
```

> "All four spine1 interfaces are down. In another terminal, let's run a continuous ping."

```bash
docker exec clab-spine-leaf-bgp-host1 ping -c 20 -i 1 10.20.4.2
```

> "A few packets lost during BGP convergence, then it recovers. Recovery is fast here because disabling an interface triggers an immediate TCP teardown -- the BGP session drops instantly. In a production fabric, you'd configure BFD -- Bidirectional Forwarding Detection -- for sub-second failure detection. Without it, BGP's default hold timer is 90 seconds, meaning it could take that long to notice a neighbor is gone. All traffic now flows through spine2. Let's check the routing table."

```bash
docker exec -it clab-spine-leaf-bgp-leaf1 sr_cli -c \
  "show network-instance default route-table ipv4-unicast summary"
```

> "The ECMP entries dropped from 2 next-hops to 1. All routes now point only to spine2 at 10.10.2.0. We lost 50% of our aggregate bandwidth, but zero connectivity. Every host can still reach every other host.
>
> Let's bring spine1 back."

```bash
docker exec -it clab-spine-leaf-bgp-spine1 sr_cli
```

```
enter candidate
set / interface ethernet-1/1 admin-state enable
set / interface ethernet-1/2 admin-state enable
set / interface ethernet-1/3 admin-state enable
set / interface ethernet-1/4 admin-state enable
commit now
exit
```

> "After a few seconds, BGP re-establishes and ECMP returns to 2 paths. The fabric healed itself -- twice. Once when spine1 went down, once when it came back. No human intervention for either event."

**Visual:** Split view -- ping output showing loss/recovery on one side, routing table showing ECMP change on the other

---

### Recap (30 seconds)

> **[VOICEOVER]**
>
> "Let's recap:
>
> - Clos spine-leaf -- named after Charles Clos's 1953 design -- is a structured 2-tier topology with predictable latency and all links active via ECMP.
> - RFC 7938 recommends eBGP for the underlay because it re-advertises routes freely without needing route reflectors. Spines share a single ASN, each leaf gets its own. Every spine-leaf link is eBGP.
> - ECMP works naturally because the shared spine ASN produces identical AS-paths through any spine. But SR Linux requires explicit multipath maximum-paths configuration to enable it.
> - Export policy chaining makes it all work: export-connected advertises host subnets, export-bgp enables transit through spines. SR Linux's default-deny export means nothing advertises without explicit policy.
> - Spine failures degrade capacity but not connectivity. Fast recovery depends on interface-level detection or BFD, not BGP's 90-second hold timer.
> - This is the architecture under every major cloud and Kubernetes deployment. When you troubleshoot pod networking, this is what's underneath."

---

### Closing (30 seconds)

> **[VOICEOVER]**
>
> "Head to the exercises folder. You'll deploy the fabric yourself, observe ECMP in the routing table, simulate a spine failure, and -- in the challenge exercise -- see how a rogue prefix can hijack traffic across the entire fabric using longest-prefix-match.
>
> This lesson gave us pure L3 routing: packets move between racks based on IP prefixes. But what about VMs and containers that need to be on the same Layer 2 subnet across different racks? That's the problem EVPN/VXLAN solves -- and that's coming next.
>
> Happy labbing!"

**Visual:** Show exercises folder, then Clos diagram with "EVPN/VXLAN overlay" teaser text

---

## Post-Recording Checklist

- [ ] Lab destroyed: `containerlab destroy --all`
- [ ] Timing verified: ~13-15 minutes
- [ ] All commands worked correctly
- [ ] Transcript updated with actual output

---

## B-Roll / Supplementary Footage Needed

1. Clos spine-leaf topology diagram with AS numbers and IP addressing
2. ECMP animation showing traffic hashing across two spines
3. Side-by-side comparison: full mesh vs 3-tier vs Clos
4. Spine failure visualization (spine going dark, traffic rerouting through remaining spine)
5. ECMP routing table transition: 2 next-hops -> 1 next-hop -> 2 next-hops

---

## Notes for Editing

- **0:00-0:30** - Hook, overlay lesson 04 topology diagram
- **0:30-2:30** - Why spine-leaf, STP comparison diagrams
- **2:30-4:00** - BGP design choices: iBGP vs eBGP, RFC 7938, shared spine ASN
- **4:00-5:30** - Our fabric: topology diagram with AS numbers and addressing
- **5:30-7:30** - Deploy fabric, show 10 containers and failed ping (no BGP yet)
- **7:30-10:30** - Configure BGP, policy chain explanation, verify sessions, ECMP routing table, pings
- **10:30-12:30** - Spine failure demo, convergence timing, ping loss/recovery, restore
- **12:30-13:00** - Recap bullet points overlay
- **13:00-13:30** - Closing, exercises call-to-action, EVPN/VXLAN teaser
